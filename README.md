# GameLang

GameLang e uma linguagem especifica de dominio para descrever regras basicas de jogos com uma sintaxe curta. Este repositorio entrega o pipeline completo solicitado no cronograma da disciplina: lexer, parser descendente, AST, analise semantica, IR serializavel, otimizacoes, interpretador, backend para Python, runtime, CLI, exemplos, testes e documentacao.

O nucleo preserva a Entrega 1: entidades globais, propriedades numericas, colisoes, dano, cura, movimento, repeticao e saida textual. O compilador valida nomes, propriedades e tipos antes de produzir IR ou Python.

## Execucao rapida

Requisito: Python 3.11 ou superior. O projeto nao usa dependencias externas em tempo de execucao.

```bash
python -m gamelang check examples/01_arena.gl
python -m gamelang run examples/01_arena.gl --touch player,enemy --json
python -m gamelang ir examples/04_otimizacoes.gl --optimize -o build/otimizado.json
python -m gamelang compile examples/02_movimento.gl --optimize -o build/movimento.py
python build/movimento.py --state-json
python -m unittest discover -s tests -v
```

Instalacao opcional do comando `gamelang`:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
gamelang run examples/03_cura.gl --json
```

## Exemplo

```gamelang
entity player {
    health = 100;
    x = 0;
    y = 0;
}

entity enemy {
    health = 30;
    x = 0;
    y = 0;
}

when player touches enemy {
    damage player by 10;
    print player.health;
}
```

O evento e acionado com `--touch player,enemy`. Colisoes sao simetricas no runtime.

## Comandos

| Comando | Resultado |
| --- | --- |
| `check` | executa lexer, parser e analise semantica |
| `tokens` | imprime tokens e posicoes em JSON |
| `ast` | imprime a AST em JSON |
| `ir` | imprime ou salva a IR serializavel |
| `run` | interpreta a IR e aceita eventos `--touch A,B` |
| `compile` | gera um modulo Python executavel |

Use `--optimize` nos comandos `ir`, `run` e `compile`. A CLI informa no fluxo de erro quantas transformacoes de cada classe foram aplicadas.

## Estrutura

```text
gamelang/              implementacao do compilador e runtime
examples/              quatro programas validos e cinco invalidos
tests/                 testes de frontend, semantica, equivalencia e otimizacao
docs/                  especificacao, arquitetura, artigo e apresentacao
```

Consulte [docs/MANUAL.md](docs/MANUAL.md) para a referencia de uso, [docs/GRAMATICA_EBNF.md](docs/GRAMATICA_EBNF.md) para a sintaxe, [docs/ARQUITETURA.md](docs/ARQUITETURA.md) para as decisoes tecnicas e [docs/LIMITACOES.md](docs/LIMITACOES.md) para o escopo conhecido.

## Criterios de aceite

- Quatro programas validos acompanham o repositorio.
- Cinco programas invalidos cobrem falhas lexicas, sintaticas e semanticas com linha e coluna.
- A analise semantica valida entidades, propriedades, duplicidades e tipos.
- Os testes comparam o interpretador e o Python gerado.
- O otimizador implementa dobramento de constantes, simplificacao algebrica e eliminacao de operacoes sem efeito.
- A IR possui formato JSON versionado e leitura de retorno.
- O pacote inclui manual, registro de IA, limitacoes, artigo e apresentacao.

## Licenca

MIT. O material academico e a autoria da equipe permanecem identificados nos documentos do projeto.

