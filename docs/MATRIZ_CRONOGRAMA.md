# Matriz de atendimento ao cronograma

| Marco do cronograma | Implementação ou evidência |
| --- | --- |
| Gramática EBNF, tokens e exemplos | `GRAMATICA_EBNF.md`, `tokens.py`, quatro exemplos válidos e cinco inválidos |
| Parser, AST e precedência | `parser.py`, `ast.py` e testes de precedência |
| Lexer e catálogo de erros | `lexer.py`, códigos L001 a L003 e posições de origem |
| Tabela de símbolos e escopos | `semantics.py`, entidades globais e propriedades por entidade |
| Tipos e testes semânticos | tipos inteiro, real, booleano, texto e posição; testes S001 a S022 |
| Registro de IA | `REGISTRO_IA.md` |
| IR e reescritas | `ir.py`, `lowering.py`, `optimizer.py` |
| Runtime e interpretador | `runtime.py`, `interpreter.py` |
| IR serializável e módulos | JSON versionado e pacote Python modular |
| Backend GameLang para Python | `backend_python.py` e arquivos em `generated/` |
| CFG, DCE e simplificações | eliminação de operações sem efeito; CFG não aplicável ao núcleo sem desvios, conforme limitações |
| Entradas adversariais e equivalência | exemplos em `examples/invalid/` e testes de snapshots |
| Pipeline completo | comando `python -m gamelang` e 27 testes automatizados |
| Metodologia e artigo | `ARTIGO_GameLang.docx` e `ARTIGO_GameLang.pdf` |
| Apresentação | `APRESENTACAO_GameLang.pptx` com 12 slides |
| Manual e entrega final | `README.md`, `MANUAL.md`, `LIMITACOES.md` e arquivo ZIP |

## Extensão opcional

O cronograma classifica Rust/PyO3 como avaliação opcional. O projeto mantém uma implementação sem dependências nativas para simplificar a reprodução. A decisão e seus efeitos estão registrados em `LIMITACOES.md`.

