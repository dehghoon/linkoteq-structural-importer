"""Read-only Core contract drift detector. Inputs must be trusted checkout files."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
import re

REQUIRED_TYPES = ("StructuralModel", "Section", "Material", "Diaphragm", "Member",
                  "Surface", "CalculatorEnvelope", "CalculatorWriteback")
REQUIRED_FILES = ("CORE_CONTRACT.md", "typescript/index.ts", "AI_GPT_UPDATE_POLICY.md")
TYPE_PATTERN = re.compile(r"^export\s+(?:interface|type)\s+([A-Za-z][A-Za-z0-9_]*)\b", re.M)

class CoreSyncError(ValueError):
    """Incomplete or untrusted Core input."""

@dataclass(frozen=True)
class CoreSnapshot:
    commit: str
    contract_version: str
    file_sha256: dict[str, str]
    exported_types: tuple[str, ...]

def snapshot_core(root: Path, *, commit: str) -> CoreSnapshot:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise CoreSyncError("A pinned 40-character lowercase Core commit is required")
    files = {}
    for name in REQUIRED_FILES:
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise CoreSyncError(f"Missing or unsafe Core file: {name}")
        data = path.read_bytes()
        if not data:
            raise CoreSyncError(f"Empty Core file: {name}")
        files[name] = sha256(data).hexdigest()
    contract = (root / "CORE_CONTRACT.md").read_text(encoding="utf-8")
    version = re.search(r"Core Contract v(\d+\.\d+)", contract)
    if version is None:
        raise CoreSyncError("Core contract version not found")
    typescript = (root / "typescript/index.ts").read_text(encoding="utf-8")
    exports = tuple(sorted(set(TYPE_PATTERN.findall(typescript))))
    missing = set(REQUIRED_TYPES) - set(exports)
    if missing:
        raise CoreSyncError(f"Missing required Core types: {sorted(missing)}")
    return CoreSnapshot(commit, version.group(1), files, exports)

def assess_core_change(approved: CoreSnapshot, candidate: CoreSnapshot) -> dict:
    """Return a deterministic review report. No automatic engineering promotion."""
    changes = sorted(name for name in REQUIRED_FILES
                     if approved.file_sha256[name] != candidate.file_sha256[name])
    removed = sorted(set(approved.exported_types) - set(candidate.exported_types))
    added = sorted(set(candidate.exported_types) - set(approved.exported_types))
    return {
        "approved_commit": approved.commit,
        "candidate_commit": candidate.commit,
        "contract_version": candidate.contract_version,
        "changed_files": changes,
        "added_types": added,
        "removed_types": removed,
        "requires_review": bool(changes or approved.contract_version != candidate.contract_version),
        "activation": "blocked" if changes or approved.contract_version != candidate.contract_version else "unchanged",
        "note": "Type presence and hashes do not establish engineering semantic compatibility."
    }

def write_report(path: Path, report: dict) -> None:
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
