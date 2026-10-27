# Arquitetura do compilador GameLang

## Pipeline

```text
fonte .gl
  -> lexer
  -> tokens com linha e coluna
  -> parser descendente e AST
  -> análise semântica e tabela de símbolos
  -> IR estruturada e serializável
  -> otimizador opcional
  -> interpretador de referência ou backend Python
  -> runtime de estado, eventos e saída
```

## Decisões

### Parser descendente

A gramática pequena e determinística favorece um parser descendente escrito à mão. A estrutura permite diagnósticos vinculados ao token corrente. Expressões usam precedência escalonada, o que evita ambiguidade sem tabelas geradas.

### AST imutável

Os nós são `dataclasses` imutáveis e carregam intervalos de origem. Essa escolha impede alterações acidentais entre parsing e análise e permite serializar a árvore para inspeção.

### Análise semântica antes da IR

A tabela de símbolos separa o escopo global de entidades do escopo local de propriedades. O analisador rejeita duplicidades, nomes ausentes e incompatibilidades antes do backend. A IR recebe apenas programas validados.

### IR estruturada

A IR conserva blocos de repetição e eventos. Cada instrução contém opcode, operandos, bloco opcional e posição de origem. O formato JSON possui o identificador `GameLang-IR` e versão `1.0`. A classe `IRProgram` implementa escrita e leitura.

### Otimizações

O módulo aplica transformações locais seguras:

1. dobramento de expressões constantes;
2. identidades algébricas, como `x + 0`, `x * 1` e `x * 0`;
3. eliminação de ações sem efeito, como cura zero, movimento `(0, 0)` e repetição zero;
4. remoção da estrutura de `repeat 1`, preservando seu corpo.

O relatório separa as classes de transformação. Os testes comparam o estado e a saída antes e depois da otimização.

### Duas rotas de execução

O interpretador executa a IR diretamente e funciona como referência. O backend emite Python legível que chama a mesma API de runtime. Os testes executam ambas as rotas e comparam um snapshot canônico do estado e da saída.

## Módulos

| Módulo | Responsabilidade |
| --- | --- |
| `lexer.py` | tokens, comentários, números, textos e posições |
| `parser.py` | declarações, instruções e precedência |
| `ast.py` | modelo sintático imutável |
| `semantics.py` | símbolos, tipos e regras de domínio |
| `ir.py` | modelo e serialização JSON |
| `lowering.py` | conversão AST para IR |
| `optimizer.py` | reescritas e relatório |
| `interpreter.py` | execução de referência |
| `backend_python.py` | geração de Python |
| `runtime.py` | entidades, eventos, colisões e saída |
| `cli.py` | interface de linha de comando |

