# Registro de uso de IA

## Objetivo

Este registro atende ao marco de uso controlado de IA do cronograma. A equipe permanece responsável pelas decisões, pela execução dos testes e pela revisão do material entregue.

## Sessão de 26 de outubro de 2026

| Campo | Registro |
| --- | --- |
| Ferramenta | Codex baseado em modelo GPT da OpenAI |
| Solicitação principal | Completar o projeto GameLang a partir da Entrega 1 e do cronograma, incluindo compilador, testes, documentação, artigo e apresentação |
| Fontes fornecidas | PDF da Entrega 1 e PDF do cronograma 2026/2 |
| Uso permitido | Estrutura inicial, implementação, casos de teste, documentação e materiais de apresentação |
| Revisão aplicada | Execução automatizada da suíte, comparação interpretador/backend, inspeção de artefatos e checagem dos critérios de aceite |
| Restrições | A IA não definiu resultados experimentais sem medi-los e não alterou o escopo central da Entrega 1 |

## Decisões revisadas

- O parser descendente foi escolhido por compatibilidade com a gramática pequena e pelos diagnósticos diretos.
- A sintaxe manteve as palavras de domínio citadas na Entrega 1: `entity`, `health`, `when`, `touches` e `damage`.
- Os requisitos adicionais do cronograma foram implementados como camadas do compilador, sem criar novos conceitos de jogabilidade.
- O runtime considera colisões simétricas e documenta essa decisão.
- As propriedades iniciais aceitam apenas expressões numéricas constantes para manter inicialização determinística.

## Verificação humana recomendada

Antes da submissão acadêmica, a equipe deve executar a suíte em uma máquina limpa, confirmar nomes e números de matrícula, revisar as citações do artigo e ensaiar a demonstração com os exemplos incluídos.

