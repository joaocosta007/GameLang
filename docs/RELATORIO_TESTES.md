# Relatório de testes e critérios de aceite

## Ambiente

- Data da execução: 26 de outubro de 2026
- Python: 3.11 ou superior
- Dependências de runtime: biblioteca padrão
- Comando: `python -m unittest discover -s tests -v`

## Cobertura funcional

| Critério | Evidência automatizada |
| --- | --- |
| Compilar ao menos três programas válidos | `test_all_valid_examples_compile` compila quatro arquivos `.gl` |
| Indicar linha e coluna em programas inválidos | testes de lexer, parser, CLI e `test_all_invalid_examples_have_positioned_diagnostics` |
| Validar nomes, escopos, propriedades e tipos | `test_semantics.py` cobre duplicidades, ausências e tipos incompatíveis |
| Equivalência entre interpretador e Python | `test_generated_python_equivalence` compara snapshots completos |
| Duas ou mais otimizações seguras | `test_optimizer.py` verifica três classes e compara comportamento |
| IR serializável | `test_ir_json_roundtrip` escreve e reconstrói o programa |

## Casos válidos

1. `01_arena.gl`: entidades, colisão, dano e saída.
2. `02_movimento.gl`: repetição, movimento e precedência.
3. `03_cura.gl`: dano, cura, movimento e referências.
4. `04_otimizacoes.gl`: dobramento, identidades e eliminação de ações sem efeito.

## Casos inválidos

1. caractere desconhecido;
2. ponto e vírgula ausente;
3. entidade inexistente;
4. propriedade inexistente;
5. movimento com tipo incompatível.

## Resultado

A execução final registrou 27 testes aprovados e nenhuma falha. A CLI também foi executada manualmente sobre os quatro programas válidos e os cinco inválidos. Os exemplos válidos produziram estado final e saída esperados. Os inválidos retornaram códigos das fases léxica, sintática ou semântica com linha e coluna.

