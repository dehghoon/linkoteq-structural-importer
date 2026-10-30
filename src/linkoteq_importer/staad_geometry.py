"""Conservative STAAD node/member extraction; never claims Core mapping.

Only explicit, independently delimited numeric records are accepted. Unsupported
syntax is retained in the source archive and reported, never silently dropped.
"""
from __future__ import annotations
from dataclasses import dataclass
import re
from .staad_lexical import LexicalResult

_NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?\Z")
_INTEGER = re.compile(r"[1-9][0-9]*\Z")
_LENGTH = {"METER", "METRE", "MM", "CM", "FEET", "FOOT", "INCH", "INCHES"}
_FORCE = {"KN", "N", "KIP", "KIPS", "LB", "LBS", "KG", "TON"}
_SECTIONS = {"JOINT COORDINATES": "nodes", "MEMBER INCIDENCES": "members"}

@dataclass(frozen=True)
class SourceNode:
    source_id: int
    xyz: tuple[float,float,float]
    length_unit: str | None
    source_line: int
    source_byte: int

@dataclass(frozen=True)
class SourceMember:
    source_id: int
    start_node: int
    end_node: int
    source_line: int
    source_byte: int

@dataclass(frozen=True)
class GeometryResult:
    nodes: tuple[SourceNode,...]
    members: tuple[SourceMember,...]
    diagnostics: tuple[str,...]
    core_mapping_status: str = "not-attempted"

def extract_geometry(lexical: LexicalResult) -> GeometryResult:
    """Extract explicit source geometry; no inferred units or node coordinates."""
    nodes: dict[int,SourceNode] = {}
    members: dict[int,SourceMember] = {}
    diagnostics: list[str] = []
    section: str | None = None
    length_unit: str | None = None
    for record in lexical.records:
        if record.classification != "statement":
            continue
        text = record.text.strip()
        # Only recognize a continuation when the previous lexical record
        # joined physical lines. This is deliberately limited to numeric data.
        if len(record.physicalSpanOrdinals) > 1:
            parts = text.splitlines()
            text = " ".join(part.rstrip().removesuffix("-").strip() for part in parts)
        for statement in text.split(";"):
            statement = statement.strip()
            if not statement:
                continue
            upper = " ".join(statement.upper().split())
            if upper.startswith("STAAD "):
                section = None
                continue
            if upper in _SECTIONS:
                section = _SECTIONS[upper]
                continue
            if upper.startswith("UNIT "):
                tokens = upper.split()
                if len(tokens) == 3 and tokens[1] in _LENGTH and tokens[2] in _FORCE:
                    length_unit = tokens[1]
                elif len(tokens) == 3 and tokens[1] in _FORCE and tokens[2] in _LENGTH:
                    length_unit = tokens[2]
                else:
                    length_unit = None
                    diagnostics.append(f"UNIT_UNVERIFIED:line={record.sourceLine}")
                continue
            if upper.startswith(("FINISH", "START ", "SUPPORTS", "MEMBER PROPERTY", "DEFINE ", "LOAD ", "LOAD COMB", "PERFORM ", "CONSTANTS", "MATERIAL ", "JOINT LOAD", "MEMBER LOAD", "ELEMENT ", "RELEASE")):
                section = None
                continue
            if section not in ("nodes", "members"):
                continue
            tokens = statement.split()
            width = 4 if section == "nodes" else 3
            # A record may have multiple explicit fixed-width tuples. TO,
            # expressions, or ambiguous tokens must be reviewed separately.
            if len(tokens) % width != 0 or not tokens:
                diagnostics.append(f"GEOMETRY_UNSUPPORTED_SYNTAX:line={record.sourceLine}")
                continue
            parsed = []
            for offset in range(0,len(tokens),width):
                chunk=tokens[offset:offset+width]
                if not _INTEGER.fullmatch(chunk[0]):
                    parsed=[];break
                if section == "nodes":
                    if not all(_NUMBER.fullmatch(x) for x in chunk[1:]):
                        parsed=[];break
                    from math import isfinite
                    coords=tuple(float(x) for x in chunk[1:])
                    if not all(isfinite(x) for x in coords):
                        parsed=[];break
                    parsed.append((int(chunk[0]),coords))
                else:
                    if not all(_INTEGER.fullmatch(x) for x in chunk[1:]):
                        parsed=[];break
                    parsed.append(tuple(int(x) for x in chunk))
            if not parsed:
                diagnostics.append(f"GEOMETRY_UNSUPPORTED_SYNTAX:line={record.sourceLine}")
                continue
            target = nodes if section == "nodes" else members
            if any(item[0] in target for item in parsed) or len({item[0] for item in parsed}) != len(parsed):
                diagnostics.append(f"DUPLICATE_SOURCE_ID:line={record.sourceLine}")
                continue
            for item in parsed:
                if section == "nodes":
                    target[item[0]] = SourceNode(item[0],item[1],length_unit,record.sourceLine,record.startByte)
                    if length_unit is None:
                        diagnostics.append(f"NODE_UNIT_UNKNOWN:id={item[0]}")
                else:
                    target[item[0]] = SourceMember(*item,record.sourceLine,record.startByte)
    for member in members.values():
        if member.start_node not in nodes or member.end_node not in nodes:
            diagnostics.append(f"MEMBER_MISSING_NODE:id={member.source_id}")
        if member.start_node == member.end_node:
            diagnostics.append(f"MEMBER_ZERO_LENGTH_TOPOLOGY:id={member.source_id}")
    return GeometryResult(tuple(nodes.values()),tuple(members.values()),tuple(dict.fromkeys(diagnostics)))
