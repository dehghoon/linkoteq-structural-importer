"""Versioned, deterministic Import Result transport for GPT-3.

This is an importer-owned envelope, NOT a new Structural Core schema.
Every source is archived independently; only verified parsed views are included.
The Core model is deliberately null until a complete mapping is validated.
"""
from __future__ import annotations
from .preservation import Archive, ArchiveError, entity_id

VERSION = "0.1.0"
STAGES = ("preserved","parsed","understood","mapped","visualized",
          "exported","analysis","equivalence")


def _source_ref(archive: Archive, kind: str, source_id: str, line: int,
                profile: str) -> dict:
    return {
        "id": entity_id(archive.namespace, profile, kind, source_id, ""),
        "sourceId": source_id, "sourceLine": line,
        "sourceHash": archive.sourceHash,
    }


def build_import_result(archive: Archive, *, format: str, limits=None) -> dict:
    """Build a safe partial source view; never silently invent Core entities."""
    if format not in ("sap2000","etabs","staad"):
        raise ArchiveError("UNSUPPORTED_IMPORT_RESULT_FORMAT")
    archive.retrieve()
    source = {"sourceHash":archive.sourceHash,"byteLength":archive.byteLength,
              "originalFilename":archive.originalFilename,
              "declaredExtension":archive.declaredExtension,
              "archiveAvailable":True}
    stage = {name:"not-attempted" for name in STAGES}
    stage["preserved"]="succeeded"
    result = {
        "contract":"linkoteq.import-result",
        "version":VERSION,
        "sourceFormat":format,
        "source":source,
        "stages":stage,
        "coreContract":"v0.5.0",
        "coreModel":None,
        "sourceViews":{"nodes":[],"frames":[],"materials":[],"sections":[],
                       "frameSectionAssignments":[],"restraints":[],"springs":[],
                       "releases":[],"loadPatterns":[],"nodalLoads":[],
                       "distributedFrameLoads":[],"loadCases":[],
                       "loadCombinations":[],"diaphragms":[]},
        "capabilities":{},
        "diagnostics":[],
        "fidelity":{"originalBytesPreserved":True,"engineeringEquivalenceVerified":False,
                    "unsupportedOrUnmappedSourceRetainedInArchive":True},
    }
    view=result["sourceViews"]
    diagnostics=result["diagnostics"]
    if format=="sap2000":
        from .sap2000_geometry import extract_geometry
        from .sap2000_properties import extract_properties
        from .sap2000_boundary import extract_boundaries
        from .sap2000_loads import extract_loads
        from .sap2000_advanced_loads import extract_advanced_loads
        g=extract_geometry(archive)
        p=extract_properties(archive)
        b=extract_boundaries(archive)
        l=extract_loads(archive)
        a=extract_advanced_loads(archive)
        profile="sap2000-tables"
        view["nodes"]=[{**_source_ref(archive,"node",j.source_id,j.source_line,profile),
                        "coordinatesSourceUnits":[str(j.x),str(j.y),str(j.z)]} for j in g.joints]
        view["frames"]=[{**_source_ref(archive,"frame",f.source_id,f.source_line,profile),
                         "startSourceId":f.joint_i,"endSourceId":f.joint_j} for f in g.frames]
        for name,items,kind in (
            ("materials",p.materials,"material"),("sections",p.sections,"section"),
            ("restraints",b.restraints,"restraint"),("springs",b.springs,"spring"),
            ("releases",b.releases,"release"),("loadPatterns",l.patterns,"load_pattern"),
            ("nodalLoads",l.joint_forces,"nodal_load"),
            ("distributedFrameLoads",a.distributed,"distributed_load"),
            ("loadCases",a.cases,"load_case"),("loadCombinations",a.combinations,"load_combination"),
            ("frameSectionAssignments",p.assignments,"frame_section_assignment"),
        ):
            for index,item in enumerate(items):
                sid=getattr(item,"source_id",None) or getattr(item,"joint_id",None) or getattr(item,"frame_id",None) or getattr(item,"combination_id",None)
                if sid is None:
                    sid=str(index)
                line=getattr(item,"source_line",None) or (item.source_lines[0] if hasattr(item,"source_lines") else 0)
                record={**_source_ref(archive,kind,str(sid),line,profile),
                        "sourceFields":{k:v for k,v in vars(item).items()
                                        if k not in ("source_line","source_lines")}}
                # Decimal is serialized as exact source text, not floating point.
                def normalize(value):
                    from decimal import Decimal
                    if isinstance(value,Decimal):return str(value)
                    if isinstance(value,tuple):return [normalize(v) for v in value]
                    if isinstance(value,dict):return {k:normalize(v) for k,v in value.items()}
                    if hasattr(value,"__dataclass_fields__"):return normalize(vars(value))
                    return value
                record["sourceFields"]=normalize(record["sourceFields"])
                view[name].append(record)
        result["sourceUnitsDeclaration"]=g.declared_units
        diagnostics.extend(g.diagnostics+p.diagnostics+b.diagnostics+l.diagnostics+a.diagnostics)
        result["capabilities"]={
            "geometry":"parsed-source-view",
            "properties":"parsed-source-view",
            "boundary":"parsed-source-view",
            "loads":"partial-source-view",
            "diaphragms":"preserved-only",
            "coreMapping":"not-attempted"}
        stage["parsed"]="partial"
    elif format=="staad":
        if limits is None:
            raise ArchiveError("STAAD_LEXICAL_LIMITS_REQUIRED")
        from .staad_lexical import lex_staad
        from .staad_geometry import extract_geometry
        lexical=lex_staad(archive,limits=limits)
        g=extract_geometry(lexical)
        profile="staad-text"
        view["nodes"]=[{**_source_ref(archive,"node",str(n.source_id),n.source_line,profile),
                        "coordinatesSourceUnits":[str(v) for v in n.xyz],
                        "lengthUnit":n.length_unit} for n in g.nodes]
        view["frames"]=[{**_source_ref(archive,"frame",str(m.source_id),m.source_line,profile),
                         "startSourceId":str(m.start_node),"endSourceId":str(m.end_node)} for m in g.members]
        diagnostics.extend(lexical.diagnostics+g.diagnostics)
        result["capabilities"]={"geometry":"partial-source-view",
                                "otherEngineering":"preserved-only","coreMapping":"not-attempted"}
        stage["parsed"]="partial"
    else:
        diagnostics.append("ETABS_ENGINEERING_PARSER_NOT_CONNECTED")
        result["capabilities"]={"engineering":"preserved-only","coreMapping":"not-attempted"}
    return result
