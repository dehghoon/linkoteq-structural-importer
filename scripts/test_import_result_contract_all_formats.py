"""Contract-level regression for all three source formats.

All input bytes in this test are authored synthetic examples, not vendor exports.
"""
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.import_result import build_import_result
from linkoteq_importer.import_result_contract import (
    validate_import_result, ImportResultContractError,
)
from test_sap2000_release_semantics import SYNTHETIC_SAP

LIMITS = Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)

def make(source, ext):
    return archive_bytes(source,filename="synthetic"+ext,extension=ext,
        project_ref="ci",namespace="ci",policy_id="test",limits=LIMITS)

def main():
    cases = (
        ("sap2000", ".s2k", SYNTHETIC_SAP),
        ("staad", ".std", b"STAAD SPACE\nUNIT METER KN\nJOINT COORDINATES\n1 0 0 0; 2 5 0 0\nMEMBER INCIDENCES\n1 1 2\nFINISH\n"),
        ("etabs", ".e2k", b"$ Synthetic ETABS placeholder, not a vendor export\n"),
    )
    for fmt, ext, source in cases:
        archive=make(source,ext)
        result=build_import_result(archive,format=fmt,limits=LIMITS)
        warnings=validate_import_result(result)
        assert result["targetCoreContract"] == "v0.6.0"
        assert result["coreMappingStatus"] == "not-validated"
        assert result["coreContract"] == "v0.5.0"  # legacy transport, not a v0.6 canonical model
        rejected={**result,"targetCoreContract":"v0.5.0"}
        try:
            validate_import_result(rejected)
        except ImportResultContractError as exc:
            assert str(exc)=="UNSUPPORTED_TARGET_CORE"
        else:
            raise AssertionError("MUST_REJECT_WRONG_CORE_TARGET")
        assert archive.retrieve()==source
        assert result["coreModel"] is None
        if fmt=="sap2000":
            assert len(result["sourceViews"]["frameEndReleaseSemantics"])==1
            release=result["sourceViews"]["frameEndReleaseSemantics"][0]
            assert release["startReleaseLocal"]["R2"] is True
            assert release["startReleaseLocal"]["R3"] is True
            assert all(not release["endReleaseLocal"][d] for d in ("U1","U2","U3","R1","R2","R3"))
        else:
            assert not result["sourceViews"]["frameEndReleaseSemantics"]
        mutated={**result,"version":"999"}
        try:
            validate_import_result(mutated)
        except ImportResultContractError as exc:
            assert str(exc)=="UNSUPPORTED_VERSION"
        else:
            raise AssertionError("MUST_REJECT_UNKNOWN_VERSION")
        print("PASS",fmt,"transport validation; warnings:",warnings)
    print("PASS all three source-format envelopes, without claiming Core mapping")

if __name__=="__main__":
    main()
