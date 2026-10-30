"""Fail-closed ingestion of approved Core catalog artifacts (offline engine).

The manifest schema is an importer integration proposal, NOT a published Core
contract. A trusted orchestrator must authenticate and supply expected hashes.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
from typing import Mapping

class CatalogSyncError(ValueError):
    """Catalog is malformed, unapproved, or incompatible."""

@dataclass(frozen=True)
class VerifiedCatalog:
    core_commit: str
    catalog_name: str
    schema_revision: int
    content_sha256: str
    record_ids: tuple[str, ...]
    records: tuple[dict, ...]

def verify_catalog(data: bytes, *, core_commit: str, expected_sha256: str,
                   catalog_name: str, approved_schema_revision: int,
                   max_bytes: int = 5_000_000, max_records: int = 100_000) -> VerifiedCatalog:
    """Verify exact bytes and explicit unit-bearing section/material records.

    No fetch, automatic promotion, conversion, or engineering calculations.
    New catalog families must receive a reviewed validator first.
    """
    if not re.fullmatch(r"[0-9a-f]{40}", core_commit):
        raise CatalogSyncError("Core commit must be a pinned lowercase SHA")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise CatalogSyncError("Expected catalog digest is invalid")
    if catalog_name not in ("sections", "materials"):
        raise CatalogSyncError("Unsupported catalog family")
    if type(approved_schema_revision) is not int or approved_schema_revision != 1:
        raise CatalogSyncError("Unapproved catalog schema revision")
    if type(data) is not bytes or type(max_bytes) is not int or not 0 < len(data) <= max_bytes:
        raise CatalogSyncError("Catalog byte limit exceeded or empty/invalid")
    if sha256(data).hexdigest() != expected_sha256:
        raise CatalogSyncError("Catalog SHA-256 mismatch")
    try:
        document = json.loads(data.decode("utf-8"), parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite")))
    except (UnicodeError, ValueError) as exc:
        raise CatalogSyncError("Catalog is not valid strict UTF-8 JSON") from exc
    if not isinstance(document, dict) or set(document) != {"core_commit", "catalog_name", "schema_revision", "records"}:
        raise CatalogSyncError("Invalid catalog envelope")
    if document["core_commit"] != core_commit or document["catalog_name"] != catalog_name or document["schema_revision"] != approved_schema_revision:
        raise CatalogSyncError("Catalog metadata does not match approved pin")
    records = document["records"]
    if not isinstance(records, list) or type(max_records) is not int or not 0 < len(records) <= max_records:
        raise CatalogSyncError("Catalog record count invalid")
    ids = set()
    required = ("A", "Iy", "Iz", "J") if catalog_name == "sections" else ("E", "G", "rho")
    validated = []
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            raise CatalogSyncError("Catalog record requires a stable nonempty id")
        if item["id"] in ids:
            raise CatalogSyncError("Duplicate catalog record id")
        ids.add(item["id"])
        if catalog_name == "sections":
            if not isinstance(item.get("name"), str) or not item["name"].strip() or set(item) != {"id", "name", "analysis"}:
                raise CatalogSyncError("Invalid section record fields")
        else:
            if not isinstance(item.get("name"), str) or not item["name"].strip() or item.get("type") not in ("steel", "concrete", "wood", "other") or set(item) != {"id", "name", "type", "analysis"}:
                raise CatalogSyncError("Invalid material record fields")
        analysis = item.get("analysis")
        expected = set(required) | ({"nu"} if catalog_name == "materials" else set())
        if not isinstance(analysis, dict) or set(analysis) != expected:
            raise CatalogSyncError("Missing or unexpected analysis properties")
        for key in required:
            value = analysis[key]
            if not isinstance(value, dict) or set(value) != {"value", "unit"} or type(value["value"]) not in (int, float) or not math.isfinite(value["value"]) or value["value"] <= 0 or not isinstance(value["unit"], str) or not value["unit"].strip():
                raise CatalogSyncError(f"Invalid explicit unit-bearing property {key}")
        if catalog_name == "materials":
            nu = analysis["nu"]
            if type(nu) not in (int, float) or not math.isfinite(nu) or not -1 < nu < 0.5:
                raise CatalogSyncError("Invalid Poisson ratio")
        validated.append(item)
    return VerifiedCatalog(core_commit, catalog_name, approved_schema_revision, expected_sha256, tuple(sorted(ids)), tuple(validated))
