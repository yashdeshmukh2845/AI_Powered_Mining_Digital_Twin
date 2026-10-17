"""Exercise the actual CLI validators with valid and deliberately invalid CSVs."""
import csv
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ["01-emas-epitermal", "02-nikel-laterit", "03-timah-placer"]


class ValidationGates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in FOLDERS:
            shutil.copytree(ROOT / folder, self.root / folder)
        shutil.copytree(ROOT / "_generator", self.root / "_generator")

    def tearDown(self):
        self.tmp.cleanup()

    def run_checker(self, script):
        return subprocess.run(
            [sys.executable, str(self.root / "_generator" / script)],
            cwd=self.root, text=True, capture_output=True,
        )

    def test_valid_committed_datasets_pass_both_checkers(self):
        for script in ["validate.py", "check_readme.py"]:
            with self.subTest(script=script):
                result = self.run_checker(script)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_negative_grade_fails_validation(self):
        path = self.root / "03-timah-placer" / "assay.csv"
        rows = list(csv.reader(io.StringIO(path.read_text())))
        rows[1][rows[0].index("SN_KGM3")] = "-1"
        with path.open("w", newline="") as file:
            csv.writer(file).writerows(rows)
        result = self.run_checker("validate.py")
        self.assertIn("GAGAL tidak ada kadar negatif", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_changed_reference_count_fails_readme_checker(self):
        path = self.root / "01-emas-epitermal" / "collar.csv"
        lines = path.read_text().splitlines()
        path.write_text("\n".join(lines + [lines[1]]) + "\n")
        result = self.run_checker("check_readme.py")
        self.assertIn("GAGAL collar", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
