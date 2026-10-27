from __future__ import annotations

from . import ast
from .diagnostics import fail
from .source import SourceSpan
from .tokens import Token, TokenKind


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def parse(self) -> ast.Program:
        entities: list[ast.EntityDecl] = []
        events: list[ast.EventDecl] = []
        statements: list[ast.Statement] = []
        start = self._current().span
        while not self._check(TokenKind.EOF):
            if self._match(TokenKind.ENTITY):
                entities.append(self._entity(self._previous()))
            elif self._match(TokenKind.WHEN):
                events.append(self._event(self._previous()))
            else:
                statements.append(self._statement())
        return ast.Program(SourceSpan.merge(start, self._current().span), tuple(entities), tuple(events), tuple(statements))

    def _entity(self, start: Token) -> ast.EntityDecl:
        name = self._consume(TokenKind.IDENT, "esperado nome da entidade")
        self._consume(TokenKind.LBRACE, "esperado '{' apos o nome da entidade")
        properties: list[tuple[str, ast.Expr, SourceSpan]] = []
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            prop = self._consume(TokenKind.IDENT, "esperado nome da propriedade")
            self._consume(TokenKind.ASSIGN, "esperado '=' apos a propriedade")
            value = self._expression()
            end = self._consume(TokenKind.SEMICOLON, "esperado ';' apos a propriedade")
            properties.append((prop.lexeme, value, SourceSpan.merge(prop.span, end.span)))
        end = self._consume(TokenKind.RBRACE, "esperado '}' para encerrar a entidade")
        return ast.EntityDecl(SourceSpan.merge(start.span, end.span), name.lexeme, tuple(properties))

    def _event(self, start: Token) -> ast.EventDecl:
        left = self._consume(TokenKind.IDENT, "esperado nome da primeira entidade")
        self._consume(TokenKind.TOUCHES, "esperado 'touches' na declaracao do evento")
        right = self._consume(TokenKind.IDENT, "esperado nome da segunda entidade")
        body, end = self._block()
        return ast.EventDecl(SourceSpan.merge(start.span, end.span), left.lexeme, right.lexeme, tuple(body))

    def _block(self) -> tuple[list[ast.Statement], Token]:
        self._consume(TokenKind.LBRACE, "esperado '{' para iniciar o bloco")
        body: list[ast.Statement] = []
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            body.append(self._statement())
        end = self._consume(TokenKind.RBRACE, "esperado '}' para encerrar o bloco")
        return body, end

    def _statement(self) -> ast.Statement:
        if self._match(TokenKind.DAMAGE):
            return self._amount_statement(ast.Damage, self._previous())
        if self._match(TokenKind.HEAL):
            return self._amount_statement(ast.Heal, self._previous())
        if self._match(TokenKind.MOVE):
            start = self._previous()
            entity = self._consume(TokenKind.IDENT, "esperado nome da entidade apos 'move'")
            self._consume(TokenKind.BY, "esperado 'by' apos a entidade")
            delta = self._expression()
            end = self._consume(TokenKind.SEMICOLON, "esperado ';' apos o movimento")
            return ast.Move(SourceSpan.merge(start.span, end.span), entity.lexeme, delta)
        if self._match(TokenKind.PRINT):
            start = self._previous()
            value = self._expression()
            end = self._consume(TokenKind.SEMICOLON, "esperado ';' apos 'print'")
            return ast.Print(SourceSpan.merge(start.span, end.span), value)
        if self._match(TokenKind.REPEAT):
            start = self._previous()
            count = self._expression()
            body, end = self._block()
            return ast.Repeat(SourceSpan.merge(start.span, end.span), count, tuple(body))
        token = self._current()
        fail("sintatico", "P004", f"instrucao inesperada: {token.lexeme or token.kind.value}", token.span)

    def _amount_statement(self, cls: type[ast.Damage] | type[ast.Heal], start: Token) -> ast.Statement:
        entity = self._consume(TokenKind.IDENT, f"esperado nome da entidade apos '{start.lexeme}'")
        self._consume(TokenKind.BY, "esperado 'by' apos a entidade")
        amount = self._expression()
        end = self._consume(TokenKind.SEMICOLON, f"esperado ';' apos '{start.lexeme}'")
        return cls(SourceSpan.merge(start.span, end.span), entity.lexeme, amount)

    def _expression(self) -> ast.Expr:
        return self._binary(1)

    PRECEDENCE = {
        TokenKind.OR: 1, TokenKind.AND: 2,
        TokenKind.EQ: 3, TokenKind.NE: 3,
        TokenKind.LT: 4, TokenKind.LE: 4, TokenKind.GT: 4, TokenKind.GE: 4,
        TokenKind.PLUS: 5, TokenKind.MINUS: 5,
        TokenKind.STAR: 6, TokenKind.SLASH: 6, TokenKind.PERCENT: 6,
    }

    def _binary(self, minimum: int) -> ast.Expr:
        left = self._unary()
        while self.PRECEDENCE.get(self._current().kind, 0) >= minimum:
            operator = self._advance()
            precedence = self.PRECEDENCE[operator.kind]
            right = self._binary(precedence + 1)
            left = ast.Binary(SourceSpan.merge(left.span, right.span), left, operator.lexeme, right)
        return left

    def _unary(self) -> ast.Expr:
        if self._match(TokenKind.MINUS, TokenKind.NOT):
            operator = self._previous()
            operand = self._unary()
            return ast.Unary(SourceSpan.merge(operator.span, operand.span), operator.lexeme, operand)
        return self._primary()

    def _primary(self) -> ast.Expr:
        if self._match(TokenKind.NUMBER, TokenKind.STRING):
            token = self._previous()
            return ast.Literal(token.span, token.value)
        if self._match(TokenKind.TRUE, TokenKind.FALSE):
            token = self._previous()
            return ast.Literal(token.span, token.kind == TokenKind.TRUE)
        if self._match(TokenKind.IDENT):
            entity = self._previous()
            self._consume(TokenKind.DOT, "referencias devem usar entidade.propriedade")
            prop = self._consume(TokenKind.IDENT, "esperado nome da propriedade apos '.'")
            return ast.PropertyRef(SourceSpan.merge(entity.span, prop.span), entity.lexeme, prop.lexeme)
        if self._match(TokenKind.LPAREN):
            start = self._previous()
            first = self._expression()
            if self._match(TokenKind.COMMA):
                second = self._expression()
                end = self._consume(TokenKind.RPAREN, "esperado ')' apos a posicao")
                return ast.Position(SourceSpan.merge(start.span, end.span), first, second)
            self._consume(TokenKind.RPAREN, "esperado ')' apos a expressao")
            return first
        token = self._current()
        fail("sintatico", "P003", "esperada expressao", token.span)

    def _current(self) -> Token:
        return self.tokens[self.index]

    def _previous(self) -> Token:
        return self.tokens[self.index - 1]

    def _advance(self) -> Token:
        token = self._current()
        if token.kind != TokenKind.EOF:
            self.index += 1
        return token

    def _check(self, kind: TokenKind) -> bool:
        return self._current().kind == kind

    def _match(self, *kinds: TokenKind) -> bool:
        if self._current().kind in kinds:
            self._advance()
            return True
        return False

    def _consume(self, kind: TokenKind, message: str) -> Token:
        if self._check(kind):
            return self._advance()
        fail("sintatico", "P001", message, self._current().span)


def parse(tokens: list[Token]) -> ast.Program:
    return Parser(tokens).parse()

