"""Fail-closed Core capability negotiation. No remote fetches or implicit promotions.

The registry is an *approved local manifest*, not an interpretation of arbitrary
Core schema additions. The caller must authenticate and pin upstream artifacts.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping


class CompatibilityError(ValueError):
    """Malformed, unapproved, or incompatible Core capability manifest."""


@dataclass(frozen=True)
class Capability:
    name: str
    kind: str
    schema_revision: int
    mapping_revision: str | None = None
    evidence_id: str | None = None


@dataclass(frozen=True)
class Registry:
    core_contract: str
    core_commit: str
    manifest_digest: str
    capabilities: tuple[Capability, ...]


@dataclass(frozen=True)
class Decision:
    name: str
    status: str
    reason: str


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def load_registry(document: Mapping[str, Any], *, expected_digest: str,
                  expected_core_commit: str, supported_contract: str) -> Registry:
    """Load a pinned, reviewed manifest; digest is supplied out-of-band.

    Digest comparison detects unexpected changes, not publisher authenticity.
    The calling deployment must authenticate the origin of expected_digest.
    """
    if not isinstance(document, dict):
        raise CompatibilityError('manifest must be an object')
    required = {'core_contract', 'core_commit', 'capabilities'}
    if set(document) != required:
        raise CompatibilityError('unexpected or missing manifest keys')
    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        raise CompatibilityError('invalid pinned digest')
    digest = sha256(canonical_bytes(document)).hexdigest()
    if digest != expected_digest:
        raise CompatibilityError('manifest digest mismatch')
    if document['core_commit'] != expected_core_commit or not isinstance(expected_core_commit, str) or not expected_core_commit:
        raise CompatibilityError('Core commit mismatch')
    if document['core_contract'] != supported_contract:
        raise CompatibilityError('unsupported Core contract')
    entries = document['capabilities']
    if not isinstance(entries, list):
        raise CompatibilityError('capabilities must be a list')
    capabilities = []
    names = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'name', 'kind', 'schema_revision', 'mapping_revision', 'evidence_id'}:
            raise CompatibilityError('invalid capability fields')
        name, kind = entry['name'], entry['kind']
        rev, mapping, evidence = entry['schema_revision'], entry['mapping_revision'], entry['evidence_id']
        if not isinstance(name, str) or not name or name in names:
            raise CompatibilityError('empty or duplicate capability name')
        if kind not in ('catalog', 'engineering'):
            raise CompatibilityError('unknown capability kind')
        if type(rev) is not int or rev < 1:
            raise CompatibilityError('invalid schema revision')
        if mapping is not None and (not isinstance(mapping, str) or not mapping):
            raise CompatibilityError('invalid mapping revision')
        if evidence is not None and (not isinstance(evidence, str) or not evidence):
            raise CompatibilityError('invalid evidence identifier')
        names.add(name)
        capabilities.append(Capability(name, kind, rev, mapping, evidence))
    return Registry(supported_contract, expected_core_commit, digest, tuple(capabilities))


def negotiate(registry: Registry, *, supported_catalog_schemas: Mapping[str, int],
              approved_engineering_mappings: Mapping[str, tuple[str, str]]) -> tuple[Decision, ...]:
    """Catalogs can be enabled by compatible schema; engineering needs exact approval.

    approved_engineering_mappings maps capability name to (mapping_revision, evidence_id).
    This function never executes vendor-to-Core mapping.
    """
    decisions = []
    for capability in registry.capabilities:
        if capability.kind == 'catalog':
            revision = supported_catalog_schemas.get(capability.name)
            enabled = type(revision) is int and revision == capability.schema_revision
            decisions.append(Decision(capability.name, 'enabled' if enabled else 'blocked',
                                      'exact catalog schema supported' if enabled else 'catalog schema unverified'))
        else:
            approved = approved_engineering_mappings.get(capability.name)
            enabled = (capability.mapping_revision is not None and capability.evidence_id is not None
                       and approved == (capability.mapping_revision, capability.evidence_id))
            decisions.append(Decision(capability.name, 'enabled' if enabled else 'blocked',
                                      'approved mapping and evidence match' if enabled else 'engineering mapping not approved'))
    return tuple(decisions)


def compare_registry(previous: Registry, current: Registry) -> dict[str, tuple[str, ...]]:
    """Describe changes only; never auto-approve them."""
    old = {c.name: c for c in previous.capabilities}
    new = {c.name: c for c in current.capabilities}
    return {
        'added': tuple(sorted(new.keys() - old.keys())),
        'removed': tuple(sorted(old.keys() - new.keys())),
        'changed': tuple(sorted(name for name in old.keys() & new.keys() if old[name] != new[name])),
    }
