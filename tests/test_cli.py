import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from gamelang.cli import main


class CliTests(unittest.TestCase):
    def test_check_valid_file(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "ok.gl"
            path.write_text("entity p { health = 1; x = 0; y = 0; }", encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(["check", str(path)])
            self.assertEqual(code, 0)
            self.assertIn("OK", out.getvalue())

    def test_invalid_file_prints_line_and_column(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "bad.gl"
            path.write_text("\nprint @;", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = main(["check", str(path)])
            self.assertEqual(code, 1)
            self.assertIn(":2:7:", err.getvalue())


if __name__ == "__main__":
    unittest.main()

