"""SAP2000 material/section catalogs and frame assignment extraction.

This is a source-referenced view, not Core mapping. All source tables remain
in the original Archive, including vendor-specific section designer details.
"""
from __future__ import annotations

from dataclasses import dataclass
from .preservation import Archive, ArchiveError
from .sap2000_geometry import iter_records, _unique


@dataclass(frozen=True)
class CatalogEntry:
    source_id: str
    fields: tuple[tuple[str, str], ...]
    source_line: int


@dataclass(frozen=True)
class FrameSectionAssignment:
    frame_id: str
    section_id: str
    material_override: str | None
    source_line: int


@dataclass(frozen=True)
class PropertyView:
    materials: tuple[CatalogEntry, ...]
    sections: tuple[CatalogEntry, ...]
    assignments: tuple[FrameSectionAssignment, ...]
    material_details: tuple[CatalogEntry, ...]
    diagnostics: tuple[str, ...]
    source_hash: str
    mapped_to_core: bool = False


def extract_properties(archive: Archive) -> PropertyView:
    materials, sections, assignments, details = [], [], [], []
    material_ids, section_ids, assigned_frames = set(), set(), set()
    diagnostics = []
    for record in iter_records(archive):
        name = record.table
        if name not in (
            "MATERIAL PROPERTIES 01 - GENERAL",
            "FRAME SECTION PROPERTIES 01 - GENERAL",
            "FRAME SECTION ASSIGNMENTS",
        ) and not name.startswith("MATERIAL PROPERTIES "):
            continue
        f = _unique(record)
        if name == "MATERIAL PROPERTIES 01 - GENERAL":
            ident = f.get("material")
            if not ident or ident in material_ids:
                raise ArchiveError(f"SAP_INVALID_MATERIAL_ID:{record.line}")
            material_ids.add(ident)
            materials.append(CatalogEntry(ident,record.fields,record.line))
        elif name == "FRAME SECTION PROPERTIES 01 - GENERAL":
            ident = f.get("sectionname")
            if not ident or ident in section_ids:
                raise ArchiveError(f"SAP_INVALID_SECTION_ID:{record.line}")
            section_ids.add(ident)
            sections.append(CatalogEntry(ident,record.fields,record.line))
        elif name == "FRAME SECTION ASSIGNMENTS":
            frame_id, section_id = f.get("frame"), f.get("analsect")
            if not frame_id or not section_id:
                raise ArchiveError(f"SAP_INCOMPLETE_SECTION_ASSIGNMENT:{record.line}")
            if frame_id in assigned_frames:
                diagnostics.append(f"REPEATED_FRAME_SECTION_ASSIGNMENT:{record.line}:{frame_id}")
            assigned_frames.add(frame_id)
            material = f.get("matprop")
            assignments.append(FrameSectionAssignment(frame_id,section_id,
                                None if material in (None,"Default") else material,
                                record.line))
        else:
            ident = f.get("material")
            if not ident:
                diagnostics.append(f"MATERIAL_DETAIL_MISSING_ID:{record.line}")
            else:
                details.append(CatalogEntry(ident,record.fields,record.line))
    for item in details:
        if item.source_id not in material_ids:
            diagnostics.append(f"UNKNOWN_MATERIAL_DETAIL:{item.source_line}:{item.source_id}")
    for item in sections:
        f = {k.casefold():v for k,v in item.fields}
        if f.get("material") and f["material"] not in material_ids:
            diagnostics.append(f"UNKNOWN_SECTION_MATERIAL:{item.source_line}:{f['material']}")
    for item in assignments:
        if item.section_id not in section_ids:
            diagnostics.append(f"UNKNOWN_ASSIGNED_SECTION:{item.source_line}:{item.section_id}")
        if item.material_override and item.material_override not in material_ids:
            diagnostics.append(f"UNKNOWN_ASSIGNED_MATERIAL:{item.source_line}:{item.material_override}")
    return PropertyView(tuple(materials),tuple(sections),tuple(assignments),
                        tuple(details),tuple(diagnostics),archive.sourceHash)
