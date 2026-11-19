"""Independent field-by-field comparison of SAP2000 source geometry with extractor."""
from pathlib import Path
from decimal import Decimal
from hashlib import sha256
import re
from linkoteq_importer.preservation import Limits, archive_bytes
from linkoteq_importer.sap2000_geometry import extract_geometry

PATH = Path("docs/MTDENN~1.$2k")
HASH = "8e31922f93485aaad44f6fae2288d29f2b9f68fdfcc158eab6af557917a5ff79"
HEADER = re.compile(r'^TABLE:\s*"([^"]+)"$', re.I)
FIELD = re.compile(r'([A-Za-z][A-Za-z0-9_]*)\s*=\s*(?:"([^"]*)"|([^\s"]+))')

def source_geometry(data):
    table, parts = None, []
    joints, frames = {}, {}
    for line in data.decode("utf-8-sig").splitlines():
        s = line.strip()
        h = HEADER.fullmatch(s)
        if h:
            assert not parts
            table = h.group(1)
            continue
        if not s or s == "END TABLE DATA":
            assert not parts
            continue
        if table is None:
            continue
        continued = s.endswith("_")
        parts.append(s[:-1].rstrip() if continued else s)
        if continued:
            continue
        record = " ".join(parts)
        parts = []
        if table not in ("JOINT COORDINATES", "CONNECTIVITY - FRAME"):
            continue
        fields = {}
        for m in FIELD.finditer(record):
            k = m.group(1).casefold()
            assert k not in fields, ("duplicate source field", k)
            fields[k] = m.group(2) if m.group(2) is not None else m.group(3)
        if table == "JOINT COORDINATES":
            key = fields["joint"]
            assert key not in joints
            joints[key] = (Decimal(fields["xorr"]), Decimal(fields["y"]), Decimal(fields["z"]))
        else:
            key = fields["frame"]
            assert key not in frames
            frames[key] = (fields["jointi"], fields["jointj"])
    assert not parts
    return joints, frames

def main():
    data = PATH.read_bytes()
    assert sha256(data).hexdigest() == HASH
    expected_joints, expected_frames = source_geometry(data)
    limits = Limits(20_000_000,200_000,200_000,2_000_000,200_000,300_000,300_000,100_000_000)
    archive = archive_bytes(data, filename=PATH.name, extension=PATH.suffix,
        project_ref="ci-fixture", namespace="ci", policy_id="read-only", limits=limits)
    actual = extract_geometry(archive)
    actual_joints = {j.source_id:(j.x,j.y,j.z) for j in actual.joints}
    actual_frames = {f.source_id:(f.joint_i,f.joint_j) for f in actual.frames}
    assert len(actual_joints) == len(actual.joints), "duplicate extracted joint"
    assert len(actual_frames) == len(actual.frames), "duplicate extracted frame"
    assert expected_joints == actual_joints, "joint IDs or coordinate values differ"
    assert expected_frames == actual_frames, "frame IDs or connectivity differ"
    assert len(expected_joints) == 388 and len(expected_frames) == 609
    print(f"PASS exact source-to-extractor comparison: {len(expected_joints)} joints, {len(expected_frames)} frames")

if __name__ == "__main__":
    main()
