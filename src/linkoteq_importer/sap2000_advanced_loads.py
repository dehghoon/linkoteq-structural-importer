"""SAP2000 distributed frame loads, load cases and combination source view.

No load combination is mapped to Core or evaluated: source semantics are
preserved and non-linear/modal/SRSS types are never treated as linear sums.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from .preservation import Archive, ArchiveError
from .sap2000_geometry import iter_records, _unique, _number


@dataclass(frozen=True)
class DistributedFrameLoad:
    frame_id: str
    pattern_id: str
    coordinate_system: str
    load_type: str
    direction: str
    distance_type: str
    start: Decimal
    end: Decimal
    magnitude_start: Decimal
    magnitude_end: Decimal
    source_line: int


@dataclass(frozen=True)
class LoadCase:
    source_id: str
    case_type: str
    fields: tuple[tuple[str, str], ...]
    source_line: int


@dataclass(frozen=True)
class CombinationTerm:
    combination_id: str
    case_or_combo_id: str
    factor: Decimal
    source_line: int


@dataclass(frozen=True)
class Combination:
    source_id: str
    combination_type: str | None
    terms: tuple[CombinationTerm, ...]
    source_lines: tuple[int, ...]
    core_linear_mapping_eligible: bool = False


@dataclass(frozen=True)
class AdvancedLoadView:
    distributed: tuple[DistributedFrameLoad, ...]
    cases: tuple[LoadCase, ...]
    combinations: tuple[Combination, ...]
    diagnostics: tuple[str, ...]
    source_hash: str
    mapped_to_core: bool = False


def extract_advanced_loads(archive: Archive) -> AdvancedLoadView:
    distributed, cases, diagnostics = [], [], []
    combo_parts: dict[str, list[CombinationTerm]] = {}
    combo_types: dict[str, str | None] = {}
    combo_lines: dict[str, list[int]] = {}
    case_ids = set()
    for record in iter_records(archive):
        table = record.table
        if table not in ("FRAME LOADS - DISTRIBUTED", "LOAD CASE DEFINITIONS",
                         "COMBINATION DEFINITIONS"):
            continue
        f = _unique(record)
        if table == "FRAME LOADS - DISTRIBUTED":
            frame, pattern = f.get("frame"), f.get("loadpat")
            system, direction = f.get("coordsys"), f.get("dir")
            distance_type = f.get("disttype")
            load_type = f.get("type")
            if not all((frame, pattern, system, direction, distance_type, load_type)):
                raise ArchiveError(f"SAP_INCOMPLETE_DISTRIBUTED_LOAD:{record.line}")
            if distance_type.casefold() == "reldist":
                a, b = "reldista", "reldistb"
            elif distance_type.casefold() == "absdist":
                a, b = "absdista", "absdistb"
            else:
                diagnostics.append(f"UNSUPPORTED_DISTANCE_TYPE:{record.line}:{distance_type}")
                continue
            distributed.append(DistributedFrameLoad(
                frame, pattern, system, load_type, direction, distance_type,
                _number(f, a, record.line), _number(f, b, record.line),
                _number(f, "foverla", record.line), _number(f, "foverlb", record.line),
                record.line))
            if system.casefold() != "global":
                diagnostics.append(f"FRAME_LOAD_COORDINATE_TRANSFORM_REQUIRED:{record.line}")
        elif table == "LOAD CASE DEFINITIONS":
            name, case_type = f.get("case"), f.get("type")
            if not name or not case_type or name in case_ids:
                raise ArchiveError(f"SAP_INVALID_LOAD_CASE:{record.line}")
            case_ids.add(name)
            cases.append(LoadCase(name, case_type, record.fields, record.line))
        else:
            name = f.get("comboname")
            if not name:
                raise ArchiveError(f"SAP_MISSING_COMBINATION_ID:{record.line}")
            combo_parts.setdefault(name, [])
            combo_lines.setdefault(name, []).append(record.line)
            if "combotype" in f:
                if name in combo_types and combo_types[name] != f["combotype"]:
                    diagnostics.append(f"CONFLICTING_COMBINATION_TYPE:{record.line}:{name}")
                combo_types[name] = f["combotype"]
            if "casename" in f:
                combo_parts[name].append(CombinationTerm(
                    name, f["casename"], _number(f, "scalefactor", record.line),
                    record.line))
            else:
                diagnostics.append(f"COMBINATION_ROW_WITHOUT_TERM:{record.line}:{name}")
    combos = []
    for name, terms in combo_parts.items():
        kind = combo_types.get(name)
        if kind is None:
            diagnostics.append(f"UNKNOWN_COMBINATION_TYPE:{name}")
        elif kind.casefold() != "linear add":
            diagnostics.append(f"NONLINEAR_OR_MODAL_COMBINATION_NOT_MAPPED:{name}:{kind}")
        combos.append(Combination(name, kind, tuple(terms), tuple(combo_lines[name])))
    names = case_ids | set(combo_parts)
    for combo in combos:
        for term in combo.terms:
            if term.case_or_combo_id not in names:
                diagnostics.append(f"UNKNOWN_COMBINATION_REFERENCE:{term.source_line}:{term.case_or_combo_id}")
    return AdvancedLoadView(tuple(distributed), tuple(cases), tuple(combos),
                            tuple(diagnostics), archive.sourceHash)
