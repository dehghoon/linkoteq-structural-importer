"""Deterministic, offline Core capability rollout planning; never activates itself."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
from .core_compatibility import Registry, Decision, compare_registry, negotiate, CompatibilityError

@dataclass(frozen=True)
class RolloutItem:
    name: str
    change: str
    decision: str
    reason: str

@dataclass(frozen=True)
class RolloutPlan:
    from_commit: str
    to_commit: str
    items: tuple[RolloutItem, ...]
    requires_review: bool


def plan_rollout(previous: Registry, candidate: Registry, *,
                 supported_catalog_schemas: Mapping[str, int],
                 approved_engineering_mappings: Mapping[str, tuple[str, str]],
                 approved_catalog_digests: Mapping[str, str] | None = None,
                 candidate_catalog_digests: Mapping[str, str] | None = None) -> RolloutPlan:
    """Fail closed: catalog *content* requires a pinned digest, not just schema.

    The caller must authenticate both registry digests and catalog digests out of band.
    This is an inspectable plan, not a deployment or a live Core connection.
    """
    if previous.core_contract != candidate.core_contract:
        raise CompatibilityError('Core contract changed: explicit migration required')
    diff = compare_registry(previous, candidate)
    changed = set(diff['changed'])
    added = set(diff['added'])
    removed = set(diff['removed'])
    decisions = {d.name: d for d in negotiate(candidate,
        supported_catalog_schemas=supported_catalog_schemas,
        approved_engineering_mappings=approved_engineering_mappings)}
    old = {c.name: c for c in previous.capabilities}
    new = {c.name: c for c in candidate.capabilities}
    approved_catalog_digests = approved_catalog_digests or {}
    candidate_catalog_digests = candidate_catalog_digests or {}
    items = []
    for name in sorted(old.keys() | new.keys()):
        if name in removed:
            items.append(RolloutItem(name, 'removed', 'blocked', 'removal requires migration review'))
            continue
        capability = new[name]
        change = 'added' if name in added else 'changed' if name in changed else 'unchanged'
        decision = decisions[name]
        if capability.kind == 'catalog' and decision.status == 'enabled':
            pinned = approved_catalog_digests.get(name)
            actual = candidate_catalog_digests.get(name)
            if not (isinstance(pinned, str) and len(pinned) == 64 and
                    all(ch in '0123456789abcdef' for ch in pinned) and actual == pinned):
                decision = Decision(name, 'blocked', 'catalog content digest not approved')
        items.append(RolloutItem(name, change, decision.status, decision.reason))
    return RolloutPlan(previous.core_commit, candidate.core_commit, tuple(items),
                       any(item.change != 'unchanged' or item.decision != 'enabled' for item in items))
