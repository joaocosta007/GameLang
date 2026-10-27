# Manual de uso da GameLang

## Requisitos e instalação

Use Python 3.11 ou superior. Entre na raiz do repositório. A execução direta não requer instalação. Para disponibilizar o comando `gamelang`, crie um ambiente virtual e execute `python -m pip install -e .`.

## Modelo da linguagem

Uma entidade possui propriedades numéricas. Ações usam o nome da entidade e eventos descrevem o que ocorre quando duas entidades se tocam.

```gamelang
entity hero {
    health = 100;
    x = 0;
    y = 0;
}
```

As propriedades `health`, `x` e `y` têm significado no runtime. Dano e cura alteram `health`; movimento altera `x` e `y`. Outras propriedades numéricas podem ser declaradas e impressas.

## Ações

```gamelang
damage hero by 10;
heal hero by 4;
move hero by (2, -1);
repeat 3 {
    move hero by (1, 0);
}
print hero.health;
print "fim";
```

## Eventos de colisão

```gamelang
when hero touches enemy {
    damage hero by 10;
    print "impacto";
}
```

Eventos ficam registrados até o runtime receber um toque. Na CLI, use `--touch hero,enemy`. O argumento pode aparecer várias vezes.

## Expressões e tipos

Há inteiros, reais, booleanos, textos e posições. Propriedades da primeira versão são numéricas. Os operadores disponíveis são `+`, `-`, `*`, `/`, `%`, comparações, igualdade, `and`, `or` e `not`.

## Inspeção do pipeline

```bash
python -m gamelang tokens examples/01_arena.gl
python -m gamelang ast examples/01_arena.gl
python -m gamelang ir examples/01_arena.gl
python -m gamelang ir examples/04_otimizacoes.gl --optimize
```

## Interpretação

```bash
python -m gamelang run examples/01_arena.gl --touch player,enemy --json
```

O programa imprime primeiro as saídas de `print`. Com `--json`, a última linha contém entidades, propriedades e saída em formato estável.

## Geração de Python

```bash
python -m gamelang compile examples/02_movimento.gl --optimize -o build/movimento.py
python build/movimento.py --state-json
```

O arquivo gerado importa `gamelang.runtime`. Execute-o a partir da raiz do projeto ou após instalar o pacote.

## Diagnósticos

Um erro segue o formato `arquivo:linha:coluna: erro fase [código]: mensagem`. A CLI usa código de saída `1` para erros da linguagem e `2` para falhas de arquivo.

## Testes

```bash
python -m unittest discover -s tests -v
```

A suíte cobre tokens, precedência, erros, nomes, tipos, serialização, runtime, backend e preservação de comportamento pelas otimizações.

