import unittest
from pathlib import Path

from gamelang.compiler import compile_file
from gamelang.diagnostics import GameLangError


ROOT = Path(__file__).resolve().parents[1]


class RepositoryExamplesTests(unittest.TestCase):
    def test_all_valid_examples_compile(self):
        examples = sorted((ROOT / "examples").glob("*.gl"))
        self.assertGreaterEqual(len(examples), 3)
        for path in examples:
            with self.subTest(path=path.name):
                compile_file(path, optimize_ir=True)

    def test_all_invalid_examples_have_positioned_diagnostics(self):
        examples = sorted((ROOT / "examples" / "invalid").glob("*.gl"))
        self.assertGreaterEqual(len(examples), 3)
        for path in examples:
            with self.subTest(path=path.name):
                with self.assertRaises(GameLangError) as context:
                    compile_file(path)
                span = context.exception.diagnostic.span
                self.assertGreaterEqual(span.line, 1)
                self.assertGreaterEqual(span.column, 1)


if __name__ == "__main__":
    unittest.main()

