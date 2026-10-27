# Gramática EBNF da GameLang

Esta gramática formaliza o escopo da Entrega 1. O parser implementa precedência por níveis e associatividade à esquerda para operadores binários.

```ebnf
programa        = { declaracao_entidade | declaracao_evento | instrucao } EOF ;

declaracao_entidade
                = "entity" identificador "{" { propriedade } "}" ;
propriedade     = identificador "=" expressao ";" ;

declaracao_evento
                = "when" identificador "touches" identificador bloco ;

bloco           = "{" { instrucao } "}" ;
instrucao       = dano | cura | movimento | repeticao | saida ;
dano            = "damage" identificador "by" expressao ";" ;
cura            = "heal" identificador "by" expressao ";" ;
movimento       = "move" identificador "by" expressao ";" ;
repeticao       = "repeat" expressao bloco ;
saida           = "print" expressao ";" ;

expressao       = disjuncao ;
disjuncao       = conjuncao { "or" conjuncao } ;
conjuncao       = igualdade { "and" igualdade } ;
igualdade       = comparacao { ( "==" | "!=" ) comparacao } ;
comparacao      = termo { ( "<" | "<=" | ">" | ">=" ) termo } ;
termo           = fator { ( "+" | "-" ) fator } ;
fator           = unaria { ( "*" | "/" | "%" ) unaria } ;
unaria          = ( "-" | "not" ) unaria | primaria ;
primaria        = numero
                | texto
                | "true"
                | "false"
                | identificador "." identificador
                | "(" expressao ")"
                | "(" expressao "," expressao ")" ;

identificador   = ( letra | "_" ) { letra | digito | "_" } ;
numero          = digito { digito } [ "." digito { digito } ] ;
texto           = '"' { caractere | escape } '"' ;
escape          = "\\n" | "\\t" | "\\\"" | "\\\\" ;
comentario      = "#" { caractere_exceto_quebra }
                | "//" { caractere_exceto_quebra } ;
```

## Precedência e associatividade

Da maior para a menor precedência: unários; multiplicação, divisão e resto; adição e subtração; comparação; igualdade; `and`; `or`. Operadores binários do mesmo nível associam à esquerda.

## Restrições semânticas

- Entidades ocupam o escopo global e não podem repetir nomes.
- Propriedades ocupam o escopo de sua entidade e não podem repetir nomes.
- Valores iniciais de propriedades são expressões numéricas constantes.
- `damage` e `heal` exigem entidade com propriedade `health` e valor numérico.
- `move` exige entidade com propriedades `x` e `y` e uma posição `(x, y)` numérica.
- `repeat` exige contagem inteira não negativa quando a contagem é conhecida em compilação.
- Referências usam sempre `entidade.propriedade`.

