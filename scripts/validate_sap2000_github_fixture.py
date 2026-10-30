"""Fail-closed source-side SAP2000 regression against the authorized GitHub fixture.

This verifies source table syntax, physical continuations and source identity.
It does not validate structural semantics, Core mapping, or IFC output.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re

EXPECTED_SHA256 = "8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
EXPECTED = {
    "tables": 72,
    "records": 9895,
    "joints": 388,
    "frames": 609,
    "sections": 84,
    "continuation_lines": 2395,
    "program_control": 1,
}
HEADER = re.compile(r'^TABLE:\s*"([^"]+)"$', re.I)
FIELD = re.compile(r'([A-Za-z][A-Za-z0-9_]*)\s*=\s*(?:"(?:[^"]|"")*"|[^\s"]+)')


def validate(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"FIXTURE_HASH_MISMATCH: {digest}")
    if b"\\x00" in data:
        raise ValueError("BINARY_FIXTURE")
    lines = data.decode("utf-8-sig").splitlines()
    table = None
    counts: Counter[str] = Counter()
    pending: list[str] = []
    continuation_lines = 0
    records = 0
    def flush() -> None:
        nonlocal records
        if not pending:
            return
        logical = " ".join(pending)
        remainder = FIELD.sub("", logical).strip()
        if remainder or not FIELD.search(logical):
            raise ValueError(f"UNRECOGNIZED_SOURCE_RECORD: {table} {records+1}")
        counts[table] += 1
        records += 1
        pending.clear()
    for line_number, original in enumerate(lines, 1):
        stripped = original.strip()
        header = HEADER.fullmatch(stripped)
        if header:
            if pending:
                raise ValueError(f"UNTERMINATED_CONTINUATION: {line_number}")
            table = header.group(1)
            counts["__tables__"] += 1
            continue
        if not stripped or stripped == "END TABLE DATA":
            if pending:
                raise ValueError(f"UNTERMINATED_CONTINUATION: {line_number}")
            continue
        if table is None:
            # SAP exports contain a free-text preamble before the first table.
            continue
        continued = stripped.endswith("_")
        if continued:
            continuation_lines += 1
        pending.append(stripped[:-1].rstrip() if continued else stripped)
        if not continued:
            flush()
    if pending:
        raise ValueError("UNTERMINATED_CONTINUATION_AT_EOF")
    actual = {
        "tables": counts["__tables__"],
        "records": records,
        "joints": counts["JOINT COORDINATES"],
        "frames": counts["CONNECTIVITY - FRAME"],
        "sections": counts["FRAME SECTION PROPERTIES 01 - GENERAL"],
        "continuation_lines": continuation_lines,
        "program_control": counts["PROGRAM CONTROL"],
    }
    if actual != EXPECTED:
        raise AssertionError(f"FIXTURE_COUNTS_MISMATCH expected={EXPECTED} actual={actual}")
    return {"sha256": digest, "counts": actual, "status": "source-lexical-only"}


def main() -> None:
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.fixture), indent=2))


if __name__ == "__main__":
    main()
