import unittest

from gamelang import ast
from gamelang.compiler import compile_source
from gamelang.diagnostics import GameLangError
from gamelang.lexer import lex
from gamelang.parser import parse
from gamelang.tokens import TokenKind


MINIMAL = """entity player {
    health = 100;
    x = 0;
    y = 0;
}
print player.health;
"""


class LexerTests(unittest.TestCase):
    def test_keywords_numbers_and_position(self):
        kinds = [token.kind for token in lex("move hero by (1, -2.5);")]
        self.assertEqual(kinds[:4], [TokenKind.MOVE, TokenKind.IDENT, TokenKind.BY, TokenKind.LPAREN])
        self.assertIn(TokenKind.NUMBER, kinds)

    def test_comments_are_ignored(self):
        tokens = lex("# comentario\n// outro\nprint 1;")
        self.assertEqual(tokens[0].kind, TokenKind.PRINT)

    def test_string_escapes(self):
        token = lex('print "a\\nb";')[1]
        self.assertEqual(token.value, "a\nb")

    def test_invalid_character_has_position(self):
        with self.assertRaises(GameLangError) as context:
            lex("\n@")
        self.assertEqual((context.exception.diagnostic.span.line, context.exception.diagnostic.span.column), (2, 1))


class ParserTests(unittest.TestCase):
    def test_builds_program(self):
        tree = parse(lex(MINIMAL))
        self.assertEqual(tree.entities[0].name, "player")
        self.assertIsInstance(tree.statements[0], ast.Print)

    def test_operator_precedence(self):
        tree = parse(lex(MINIMAL.replace("100", "2 + 3 * 4")))
        expression = tree.entities[0].properties[0][1]
        self.assertEqual(expression.operator, "+")
        self.assertEqual(expression.right.operator, "*")

    def test_missing_semicolon_has_position(self):
        with self.assertRaises(GameLangError) as context:
            compile_source(MINIMAL.replace("health = 100;", "health = 100"))
        self.assertEqual(context.exception.diagnostic.phase, "sintatico")
        self.assertGreater(context.exception.diagnostic.span.line, 1)


if __name__ == "__main__":
    unittest.main()

