# Limitações conhecidas da GameLang

## Escopo intencional

A versão 1 implementa o domínio descrito na Entrega 1. Ela não tenta substituir uma engine de jogos. Não há renderização gráfica, áudio, física contínua, rede, entrada de teclado ou relógio de quadro.

## Linguagem

- Propriedades de entidades são numéricas e recebem valores constantes na declaração.
- Não há funções definidas pelo usuário, variáveis locais, módulos ou importações.
- Não há condicionais. Booleanos existem em expressões e na análise de tipos, mas o núcleo não inclui uma instrução `if`.
- `repeat` executa de forma síncrona e pode consumir tempo ou memória quando recebe contagens muito grandes.
- Divisão por zero em uma expressão dependente do estado aparece em execução. O otimizador evita dobrar esse caso.
- Textos suportam apenas os escapes `\\n`, `\\t`, `\\"` e `\\\\`.

## Runtime

- O evento `touches` depende de eventos informados ao runtime. Não há detecção geométrica automática.
- Dano pode reduzir `health` abaixo de zero e cura não possui limite máximo.
- Movimento soma deltas às propriedades `x` e `y`; não há velocidade, colisão espacial ou unidade física.
- Eventos de colisão são simétricos. A ordem escrita não altera o disparo.

## Backend e portabilidade

- O Python gerado depende do módulo `gamelang.runtime`, portanto deve rodar no repositório ou com o pacote instalado.
- A IR estruturada facilita inspeção e serialização, mas não usa SSA e não constrói um CFG explícito porque a linguagem não possui desvios condicionais.
- A extensão Rust/PyO3 citada no cronograma permanece opcional e não foi incluída. O projeto não exige compilador nativo.

## Avaliação de desempenho

As otimizações reduzem nós da IR e operações sem efeito. O projeto demonstra preservação de comportamento, mas não afirma ganho universal de tempo. Entradas pequenas são dominadas pelo custo de inicialização do Python.

