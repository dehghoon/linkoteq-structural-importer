"""Pinned SAP2000 regression: distributed loads, cases and combination semantics."""
from hashlib import sha256
from pathlib import Path

from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_loads import extract_loads
from linkoteq_importer.sap2000_advanced_loads import extract_advanced_loads


def main():
    path = Path("docs/MTDENN~1.$2k")
    data = path.read_bytes()
    assert sha256(data).hexdigest() == "8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    archive = archive_bytes(data, filename=path.name, extension=path.suffix,
        project_ref="ci-fixture", namespace="ci", policy_id="read-only",
        limits=Limits(20_000_000, 200_000, 200_000, 2_000_000, 200_000,
                      300_000, 300_000, 100_000_000))
    geometry = extract_geometry(archive)
    base = extract_loads(archive)
    advanced = extract_advanced_loads(archive)
    frame_ids = {frame.source_id for frame in geometry.frames}
    pattern_ids = {pattern.source_id for pattern in base.patterns}
    assert advanced.distributed, "no distributed frame loads extracted"
    assert advanced.cases, "no load cases extracted"
    assert advanced.combinations, "no combinations extracted"
    assert all(load.frame_id in frame_ids for load in advanced.distributed), "unknown frame"
    assert all(load.pattern_id in pattern_ids for load in advanced.distributed), "unknown load pattern"
    assert all(combo.core_linear_mapping_eligible is False for combo in advanced.combinations)
    assert not advanced.mapped_to_core
    assert archive.retrieve() == data
    print(f"PASS: distributed={len(advanced.distributed)} cases={len(advanced.cases)} "
          f"combinations={len(advanced.combinations)} diagnostics={len(advanced.diagnostics)}")
    for diagnostic in advanced.diagnostics[:25]:
        print("DIAGNOSTIC:", diagnostic)


if __name__ == "__main__":
    main()
