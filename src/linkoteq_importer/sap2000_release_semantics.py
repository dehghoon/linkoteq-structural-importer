"""Conservative SAP2000 release interpretation for the GPT-3 handoff.

SAP frame end releases are member-local, ordered P,V2,V3,T,M2,M3.
Do not reinterpret as global DOFs or silently infer physical hinges.
"""
from __future__ import annotations
from dataclasses import dataclass
from .sap2000_boundary import FrameRelease
from .sap2000_frame_axes import FrameAxisView

SAP_END_KEYS=("P","V2","V3","T","M2","M3")
CORE_LOCAL_DOFS=("U1","U2","U3","R1","R2","R3")

@dataclass(frozen=True)
class ReleaseInterpretation:
    frame_id: str
    start: dict[str,bool]
    end: dict[str,bool]
    source_line: int
    local_axis_angle_degrees: str | None
    status: str
    warnings: tuple[str,...]

def interpret_release(record:FrameRelease, axes:FrameAxisView) -> ReleaseInterpretation:
    """No global-axis transformation; do not synthesize missing axis rotation."""
    if len(record.released)!=12:
        raise ValueError("EXPECTED_12_SAP_RELEASE_FLAGS")
    matching=[a for a in axes.rotations if a.frame_id==record.frame_id]
    warnings=[]
    if len(matching)>1:
        warnings.append("DUPLICATE_LOCAL_AXIS_ROTATION")
    if not matching:
        warnings.append("NO_EXPLICIT_LOCAL_AXIS_ROTATION")
    angle=str(matching[0].angle_degrees) if len(matching)==1 else None
    return ReleaseInterpretation(
        record.frame_id,
        dict(zip(CORE_LOCAL_DOFS,record.released[:6])),
        dict(zip(CORE_LOCAL_DOFS,record.released[6:])),
        record.source_line,angle,
        "source-local-interpretation-not-core-mapped",tuple(warnings))
