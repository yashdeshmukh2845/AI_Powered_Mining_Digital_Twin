import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package_snapshot", ROOT / "_generator/package_snapshot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Snapshot(unittest.TestCase):
    def test_reproducible_archive_and_known_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            archive = module.package(ROOT, output, "tested-revision")
            first = archive.read_bytes()
            self.assertEqual(first, module.package(ROOT, output, "tested-revision").read_bytes())
            with zipfile.ZipFile(archive) as zip_file:
                zip_file.extractall(output / "unpacked")
            manifest = module.verify(output / "unpacked")
            self.assertEqual(manifest["source_ref"], "tested-revision")
            for folder, count in zip(module.DATASETS, (103, 350, 500)):
                self.assertEqual(manifest["files"][folder + "/collar.csv"]["rows"], count)
            self.assertEqual(len([name for name in manifest["files"] if name.endswith(".csv")]), 12)

    def test_modified_data_and_missing_table_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = module.package(ROOT, root, "test")
            with zipfile.ZipFile(archive) as zip_file:
                zip_file.extractall(root)
            path = root / "02-nikel-laterit/assay.csv"
            original = path.read_bytes()
            path.write_bytes(original.replace(b"0", b"1", 1))
            with self.assertRaisesRegex(ValueError, "Snapshot differs"):
                module.verify(root)
            path.write_bytes(original)
            manifest_path = root / "DATA-MANIFEST.json"
            manifest = json.loads(manifest_path.read_text())
            del manifest["files"]["02-nikel-laterit/assay.csv"]
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "twelve training CSVs"):
                module.verify(root)


if __name__ == "__main__":
    unittest.main()
