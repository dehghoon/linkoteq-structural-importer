"""Deterministic risk-based representative selection; pure Python, format-agnostic.

Selection is for manual/vendor-reviewed golden samples, not full-record automated validation.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Candidate:
    source_id: str
    classes: tuple[str, ...]
    high_risk: tuple[str, ...] = ()

@dataclass(frozen=True)
class Selection:
    selected_ids: tuple[str, ...]
    class_counts: dict[str, int]
    target_by_class: dict[str, int]
    uncovered: tuple[str, ...]
    reasons: dict[str, tuple[str, ...]]

def select_samples(candidates: Iterable[Candidate]) -> Selection:
    rows = sorted(tuple(candidates), key=lambda c: c.source_id)
    ids = [r.source_id for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate source_id")
    counts: dict[str,int] = {}
    highs: set[str] = set()
    for row in rows:
        if len(set(row.classes)) != len(row.classes):
            raise ValueError("duplicate class on record")
        if not set(row.high_risk).issubset(row.classes):
            raise ValueError("high_risk must be a subset of classes")
        for name in row.classes:
            counts[name] = counts.get(name,0)+1
        highs.update(row.high_risk)
    targets = {name: min(count, 2 if name in highs else 1) for name,count in counts.items()}
    covered = {name:0 for name in counts}
    chosen: list[Candidate] = []
    remaining = rows[:]
    while any(covered[name]<target for name,target in targets.items()):
        def gain(row:Candidate):
            missing = [name for name in row.classes if covered[name]<targets[name]]
            return (sum(2 if name in highs else 1 for name in missing),len(missing))
        best = max(remaining,key=gain)
        if gain(best)[0]==0:
            break
        chosen.append(best)
        remaining.remove(best)
        for name in best.classes:
            covered[name]+=1
    reasons={r.source_id:tuple(sorted(r.classes)) for r in chosen}
    return Selection(tuple(r.source_id for r in chosen),counts,targets,
                     tuple(sorted(name for name,target in targets.items() if covered[name]<target)),reasons)
