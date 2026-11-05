"""Real SAP2000 GPT-3 handoff integration and JSON round-trip regression."""
from __future__ import annotations

from base64 import b64decode
from hashlib import sha256
from json import loads
from pathlib import Path

from linkoteq_importer.sap2000_gpt3_package import build_gpt3_package, package_to_json


def run() -> None:
    source = Path("docs/MTDENN~1.$2k").read_bytes()
    expected_hash = "8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
    assert sha256(source).hexdigest() == expected_hash
    package = build_gpt3_package(source, filename="MTDENN~1.$2k",
                                 project_id="real-sap-fixture")
    assert package["sourceHash"] == expected_hash
    assert package["coreModel"] is None
    assert not package["canonicalMappingValidated"]
    assert not package["analysisReady"]
    geometry = package["geometryPreview"]
    assert len(geometry["nodes"]) == 388
    assert len(geometry["members"]) == 609
    assert all(member["renderable"] for member in geometry["members"])
    grids = geometry["grids"]
    assert len(grids["gridLines"]) + len(grids["deferredGridLines"]) == 31
    assert geometry["sourceLevels"]["sourceRecordCount"] == 0
    assert all(not level["sourceDefined"] for level in geometry["inferredLevels"])
    loads = package["engineeringData"]["sourceLoads"]
    assert len(loads["distributedFrameLoads"]) == 1810
    assert len(loads["loadCases"]) == 11
    assert len(loads["loadCombinations"]) == 48
    assert b64decode(package["sourceArchive"]["bytesBase64"], validate=True) == source
    encoded = package_to_json(package)
    decoded = loads_json(encoded)
    assert decoded["sourceHash"] == expected_hash
    assert decoded["coreModel"] is None
    assert len(decoded["geometryPreview"]["members"]) == 609
    assert len(decoded["engineeringData"]["sourceLoads"]["distributedFrameLoads"]) == 1810
    print("SAP_GPT3_HANDOFF_PASS", len(encoded), len(grids["gridLines"]),
          len(grids["deferredGridLines"]), len(geometry["inferredLevels"]))


def loads_json(value: str) -> dict:
    return loads(value)


if __name__ == "__main__":
    run()
