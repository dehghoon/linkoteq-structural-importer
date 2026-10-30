"""Read-only, fail-closed Core drift report from immutable Git commit objects."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def _git(core: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(core), *args], check=True,
                          capture_output=True, timeout=30).stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from linkoteq_importer.core_sync import (REQUIRED_FILES, CoreSyncError,
                                             assess_core_change, snapshot_core)
    report: dict = {"activation": "blocked", "requires_review": True,
                    "status": "error", "baseline": args.baseline,
                    "candidate": args.candidate}
    exit_code = 3
    try:
        # Resolve refs to exact commit objects; refuse tags, branch names and prefixes.
        import re
        if any(not re.fullmatch(r"[0-9a-f]{40}", ref)
               for ref in (args.baseline, args.candidate)):
            raise CoreSyncError("Full lowercase 40-character commit SHAs required")
        for ref in (args.baseline, args.candidate):
            if _git(args.core, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip() != ref:
                raise CoreSyncError("Reference is not the specified immutable commit")
        def snapshot(ref: str):
            with TemporaryDirectory() as directory:
                tmp = Path(directory)
                for name in REQUIRED_FILES:
                    target = tmp / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(_git(args.core, "show", f"{ref}:{name}"))
                return snapshot_core(tmp, commit=ref)
        approved, candidate = snapshot(args.baseline), snapshot(args.candidate)
        report = assess_core_change(approved, candidate)
        report["status"] = "review-required" if report["requires_review"] else "unchanged"
        exit_code = 2 if report["requires_review"] else 0
    except (CoreSyncError, OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)[:400]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
