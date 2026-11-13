"""Source-only SAP2000 area polygon preview; no certified shell properties."""
from __future__ import annotations

from .sap2000_geometry import iter_records, _unique
from .preservation import ArchiveError


def extract_area_preview(archive) -> dict:
    areas = []
    seen = set()
    for record in iter_records(archive):
        if record.table != "CONNECTIVITY - AREA":
            continue
        fields = _unique(record)
        area_id = fields.get("area")
        if not area_id or area_id in seen:
            raise ArchiveError(f"SAP_DUPLICATE_OR_MISSING_AREA:{record.line}")
        seen.add(area_id)
        joint_fields = [(int(key[5:]), value) for key, value in fields.items()
                        if key.startswith("joint") and key[5:].isdigit()]
        joint_fields.sort()
        joint_ids = [value for _, value in joint_fields]
        if len(joint_ids) < 3 or len(set(joint_ids)) != len(joint_ids):
            raise ArchiveError(f"SAP_INVALID_AREA_BOUNDARY:{record.line}:{area_id}")
        areas.append({"sourceId": area_id, "boundaryNodeIds": joint_ids,
                      "sourceLine": record.line, "geometryOnly": True})
    return {"areas": areas, "analysisReady": False, "mappingValidated": False}
