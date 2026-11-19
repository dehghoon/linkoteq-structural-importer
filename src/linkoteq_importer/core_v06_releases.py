"""SAP2000 frame-end binary release mapping to Core v0.6.

SAP source order is P,V2,V3,T,M2,M3 at I and J. For a member-local
right-handed frame this corresponds to DX,DY,DZ,RX,RY,RZ at each end.
This maps only binary releases; partial fixity/stiffness and axis rotation
must be separately reviewed and are never silently synthesized.
"""
from __future__ import annotations

DOFS = ("DX", "DY", "DZ", "RX", "RY", "RZ")

def map_binary_frame_releases_v06(boundaries, geometry) -> dict:
    if boundaries.source_hash != geometry.source_hash:
        raise ValueError("SOURCE_HASH_MISMATCH")
    frames = {frame.source_id for frame in geometry.frames}
    members = []
    diagnostics = []
    seen = set()
    for release in boundaries.releases:
        frame_id = release.frame_id
        if frame_id in seen:
            raise ValueError("DUPLICATE_FRAME_RELEASE:" + frame_id)
        seen.add(frame_id)
        if frame_id not in frames:
            diagnostics.append("UNKNOWN_RELEASE_MEMBER:" + frame_id)
            continue
        values = release.released
        if len(values) != 12 or any(type(v) is not bool for v in values):
            diagnostics.append("INVALID_FRAME_RELEASE:" + frame_id)
            continue
        members.append({
            "memberId": "sap2000:member:" + frame_id,
            "startRelease": dict(zip(DOFS, values[:6])),
            "endRelease": dict(zip(DOFS, values[6:])),
            "sourceLine": release.source_line,
        })
    return {
        "targetSchemaVersion": "0.6",
        "sourceHash": geometry.source_hash,
        "members": members,
        "diagnostics": diagnostics,
        "status": "blocked" if diagnostics else "binary-release-subset-unvalidated",
        "canonicalMappingValidated": False,
        "omittedDomains": ["partial-fixity-stiffness", "release-local-axis-verification",
                           "insertion-offsets", "member-end-spring-stiffness"],
    }
