"""Optional regression for the real SCIENC SAP2000 fixture.

Set SCIENC_FIXTURE to the local .s2k / .$2k file.  This test deliberately
does not assume geometry counts before the real parser has been verified.
"""
from __future__ import annotations

import os
from base64 import b64decode
from hashlib import sha256
from pathlib import Path

import pytest

from linkoteq_importer.sap2000_gpt3_package import build_gpt3_package, package_to_json


def test_scienc_lossless_handoff():
    fixture = os.environ.get("SCIENC_FIXTURE")
    if not fixture:
        pytest.skip("Set SCIENC_FIXTURE to the real SCIENC~1.$2k file")
    path = Path(fixture)
    source = path.read_bytes()
    expected_sha = "2473e11206a75d0145ffaabc471ad2ef939c54bd8e58ef8883fc1dc6fd2275a3"
    assert sha256(source).hexdigest() == expected_sha, "Wrong regression fixture"

    package = build_gpt3_package(source, filename=path.name, project_id="scienc-regression")
    assert package["sourceHash"] == expected_sha
    assert package["analysisReady"] is False
    assert package["canonicalMappingValidated"] is False
    assert package["sourceArchive"]["byteLength"] == len(source)
    assert b64decode(package["sourceArchive"]["bytesBase64"], validate=True) == source
    assert package["geometryPreview"]["nodes"], "No nodes parsed"
    assert package["geometryPreview"]["members"], "No members parsed"

    import json
    serialized = json.loads(package_to_json(package))
    assert serialized["sourceArchive"]["sha256"] == expected_sha
    assert serialized["geometryPreview"] == json.loads(
        json.dumps(package["geometryPreview"], default=str)
    )
