import unittest

from gamelang.compiler import compile_source
from gamelang.diagnostics import GameLangError


BASE = """entity p {
    health = 10;
    x = 0;
    y = 0;
}
"""


class SemanticTests(unittest.TestCase):
    def assert_code(self, source, code):
        with self.assertRaises(GameLangError) as context:
            compile_source(source)
        self.assertEqual(context.exception.diagnostic.code, code)
        self.assertGreaterEqual(context.exception.diagnostic.span.line, 1)
        self.assertGreaterEqual(context.exception.diagnostic.span.column, 1)

    def test_duplicate_entity(self):
        self.assert_code(BASE + BASE, "S001")

    def test_duplicate_property(self):
        self.assert_code("entity p { health = 1; health = 2; }", "S002")

    def test_property_must_be_numeric(self):
        self.assert_code('entity p { health = "muita"; }', "S003")

    def test_unknown_entity(self):
        self.assert_code(BASE + "damage ghost by 1;", "S005")

    def test_unknown_property(self):
        self.assert_code(BASE + "print p.mana;", "S006")

    def test_move_requires_position(self):
        self.assert_code(BASE + "move p by 2;", "S012")

    def test_repeat_requires_integer(self):
        self.assert_code(BASE + "repeat 2.5 { print 1; }", "S013")

    def test_negative_repeat_is_rejected(self):
        self.assert_code(BASE + "repeat -1 { print 1; }", "S014")


if __name__ == "__main__":
    unittest.main()

