"""Real pinned SAP fixture test for six-DOF support mapping."""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.core_v06_supports import map_global_restraints_v06, DOFS

def run():
    data = Path("docs/MTDENN~1.$2k").read_bytes()
    digest = "8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    assert sha256(data).hexdigest() == digest
    limits = Limits(20_000_000, 200_000, 200_000, 2_000_000,
                    200_000, 300_000, 300_000, 100_000_000)
    archive = archive_bytes(data, filename="MTDENN~1.$2k", extension=".$2k",
                            project_ref="ci-fixture", namespace="ci",
                            policy_id="read-only", limits=limits)
    geometry = extract_geometry(archive)
    boundaries = extract_boundaries(archive)
    result = map_global_restraints_v06(boundaries, geometry)
    assert result["targetSchemaVersion"] == "0.6"
    assert len(boundaries.restraints) == 55
    assert len(result["supports"]) == 55
    assert result["diagnostics"] == []
    assert not result["canonicalMappingValidated"]
    source = {r.joint_id: r.fixed for r in boundaries.restraints}
    for support in result["supports"]:
        node_id = support["nodeId"].removeprefix("sap2000:node:")
        assert tuple(support["restraints"][d] for d in DOFS) == source[node_id]
    assert archive.retrieve() == data
    print("PASS real SAP fixture 55/55 six-DOF restraints mapped without loss")

if __name__ == "__main__":
    run()
