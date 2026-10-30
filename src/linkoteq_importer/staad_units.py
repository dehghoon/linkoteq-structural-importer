"""Explicit STAAD length-unit normalization into a review-only geometry IR.

This is not a canonical Core mapping. It does not infer missing source units,
structural member properties, or force/mass semantics.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from math import isfinite, sqrt
from .staad_geometry import GeometryResult

# Exact international length definitions. 1 international foot = 0.3048 m.
_TO_METERS = {
    "METER": Decimal("1"), "METRE": Decimal("1"),
    "MM": Decimal("0.001"), "CM": Decimal("0.01"),
    "FEET": Decimal("0.3048"), "FOOT": Decimal("0.3048"),
    "INCH": Decimal("0.0254"), "INCHES": Decimal("0.0254"),
}

@dataclass(frozen=True)
class NormalizedNode:
    source_id: int
    xyz_m: tuple[float, float, float]
    source_unit: str
    source_line: int
    source_byte: int

@dataclass(frozen=True)
class NormalizedMember:
    source_id: int
    start_node: int
    end_node: int
    length_m: float
    source_line: int
    source_byte: int

@dataclass(frozen=True)
class NormalizedGeometry:
    nodes: tuple[NormalizedNode, ...]
    members: tuple[NormalizedMember, ...]
    diagnostics: tuple[str, ...]
    mapping_status: str = "not-attempted"
    unit_system: str = "meter"


def normalize_geometry(geometry: GeometryResult) -> NormalizedGeometry:
    """Normalize only explicit, finite length units; quarantine invalid members.

    A missing or invalid unit never becomes a default. Source data stays in the
    independent archive. Coordinates are converted before length calculation.
    """
    diagnostics = list(geometry.diagnostics)
    nodes: dict[int, NormalizedNode] = {}
    for node in geometry.nodes:
        factor = _TO_METERS.get(node.length_unit or "")
        if factor is None:
            diagnostics.append(f"NODE_UNIT_NOT_CONVERTIBLE:id={node.source_id}")
            continue
        try:
            converted = tuple(float(Decimal(str(value)) * factor) for value in node.xyz)
        except (InvalidOperation, OverflowError, ValueError):
            diagnostics.append(f"NODE_CONVERSION_INVALID:id={node.source_id}")
            continue
        if not all(isfinite(v) for v in converted):
            diagnostics.append(f"NODE_CONVERSION_NONFINITE:id={node.source_id}")
            continue
        nodes[node.source_id] = NormalizedNode(node.source_id, converted,
            node.length_unit, node.source_line, node.source_byte)
    members: list[NormalizedMember] = []
    for member in geometry.members:
        a, b = nodes.get(member.start_node), nodes.get(member.end_node)
        if a is None or b is None:
            diagnostics.append(f"MEMBER_NORMALIZATION_BLOCKED:id={member.source_id}")
            continue
        delta = tuple(y - x for x, y in zip(a.xyz_m, b.xyz_m))
        length = sqrt(sum(d * d for d in delta))
        if not isfinite(length) or length <= 0:
            diagnostics.append(f"MEMBER_LENGTH_INVALID:id={member.source_id}")
            continue
        members.append(NormalizedMember(member.source_id, member.start_node,
            member.end_node, length, member.source_line, member.source_byte))
    return NormalizedGeometry(tuple(nodes.values()), tuple(members),
                              tuple(dict.fromkeys(diagnostics)))
