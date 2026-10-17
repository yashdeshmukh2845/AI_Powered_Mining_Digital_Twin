"""Create and verify a versioned teaching-data ZIP (standard library only)."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "01-emas-epitermal": {"seed": 20260829, "epsg": 32748, "grade_units": {"AU_GPT": "g/t", "AG_GPT": "g/t", "SG": "t/m3"}},
    "02-nikel-laterit": {"seed": 20260830, "epsg": 32751, "grade_units": {"NI_PCT": "%", "CO_PCT": "%", "FE_PCT": "%", "MGO_PCT": "%", "SIO2_PCT": "%", "AL2O3_PCT": "%", "CR2O3_PCT": "%", "SG": "t/m3"}},
    "03-timah-placer": {"seed": 20260831, "epsg": 32748, "grade_units": {"SN_KGM3": "kg/m3", "BD_TM3": "t/m3"}},
}
TABLES = ("collar", "survey", "assay", "litho")


def payload(root):
    paths = [f"{folder}/{table}.csv" for folder in DATASETS for table in TABLES]
    paths += [f"{folder}/README.md" for folder in DATASETS]
    paths += ["README.md", "LICENSE.txt", "CITATION.cff", "docs/USE_WITH_GEOSUITE.md"]
    paths += [p.relative_to(root).as_posix() for p in sorted((root / "_generator").glob("*.py"))]
    paths += ["_generator/requirements.txt"]
    return {name: (root / name).read_bytes() for name in sorted(paths)}


def make_manifest(files, source_ref):
    citation = files["CITATION.cff"].decode()
    version = re.search(r"^version:\s*['\"]?([^'\"\s]+)", citation, re.M).group(1)
    records = {}
    for name, data in files.items():
        record = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if name.endswith(".csv"):
            rows = list(csv.reader(io.StringIO(data.decode("utf-8"))))
            record.update({"columns": rows[0], "rows": len(rows) - 1})
        records[name] = record
    return {"schema_version": 1, "version": version, "source_ref": source_ref,
            "synthetic": True, "license": "CC-BY-4.0", "datasets": DATASETS,
            "coordinate_unit": "m", "depth_unit": "m", "dip_convention": "positive down; 90 = vertical",
            "missing_value": "blank; never replace with zero implicitly", "files": records}


def verify(root):
    manifest = json.loads((root / "DATA-MANIFEST.json").read_text())
    if manifest.get("schema_version") != 1 or manifest.get("synthetic") is not True:
        raise ValueError("Unsupported snapshot manifest")
    expected_csv = {f"{folder}/{table}.csv" for folder in DATASETS for table in TABLES}
    if {name for name in manifest["files"] if name.endswith(".csv")} != expected_csv:
        raise ValueError("Snapshot must contain the twelve training CSVs")
    for name, record in manifest["files"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe manifest path")
        data = (root / path).read_bytes()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError("Snapshot differs from manifest: " + name)
        if name.endswith(".csv"):
            rows = list(csv.reader(io.StringIO(data.decode("utf-8"))))
            if rows[0] != record["columns"] or len(rows) - 1 != record["rows"]:
                raise ValueError("CSV schema/count differs: " + name)
    return manifest


def package(root, output, source_ref="local-unrecorded"):
    files = payload(root)
    manifest = make_manifest(files, source_ref)
    files["DATA-MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"orebit-datasets-{manifest['version']}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zip_file.writestr(info, data, compresslevel=9)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_text(f"{checksum}  {archive.name}\n")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts")
    parser.add_argument("--source-ref", default="local-unrecorded")
    parser.add_argument("--verify", type=Path, help="Verify an extracted snapshot against its manifest")
    args = parser.parse_args()
    if args.verify:
        result = verify(args.verify)
        print(f"PASS: snapshot {result['version']}, source {result['source_ref']}")
    else:
        print(package(ROOT, args.output, args.source_ref))
