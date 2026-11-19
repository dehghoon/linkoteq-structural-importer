"""Real SAP2000 regression: all binary I/J release flags retained."""
from hashlib import sha256
from pathlib import Path
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry
from linkoteq_importer.sap2000_boundary import extract_boundaries
from linkoteq_importer.core_v06_releases import map_binary_frame_releases_v06, DOFS

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
    result = map_binary_frame_releases_v06(boundaries, geometry)
    assert len(boundaries.releases) == 180
    assert len(result["members"]) == 180
    assert result["diagnostics"] == []
    assert not result["canonicalMappingValidated"]
    source = {r.frame_id: r.released for r in boundaries.releases}
    for member in result["members"]:
        frame_id = member["memberId"].removeprefix("sap2000:member:")
        original = source[frame_id]
        assert tuple(member["startRelease"][d] for d in DOFS) == original[:6]
        assert tuple(member["endRelease"][d] for d in DOFS) == original[6:]
    assert archive.retrieve() == data
    print("PASS real SAP fixture 180/180 binary I/J releases preserved in Core v0.6 shape")

if __name__ == "__main__":
    run()
