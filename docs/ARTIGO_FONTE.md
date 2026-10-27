# GameLang: Uma linguagem específica de domínio para regras básicas de jogos

**Autores:**  
Victor Will dos Santos (194427) · João Pedro Pirani (194411) · Ryan Markus Maciel Araujo (202006) · Lucas dos Santos Garreto (200131) · Enzo Giuliano Cardoso Santana (200265)

**Instituição:**  
Ciência da Computação, Centro Universitário Adventista de São Paulo (UNASP-SP) · Projeto e Implementação de Compiladores · 2026/2

## Resumo

A GameLang é uma linguagem específica de domínio para descrever regras básicas de jogos por meio de entidades, eventos de colisão, dano, cura, movimento, repetição e saída textual. Este artigo apresenta sua implementação em Python e avalia a verificação semântica com uma bateria controlada: 26 programas sintaticamente válidos contendo erros semânticos deliberados e oito programas corretos usados como controles. O compilador rejeitou os 26 casos inválidos e aceitou os oito controles; não houve erro escapado nem falso positivo nesse conjunto. O projeto também inclui análise léxica e sintática, árvore sintática, tabela de símbolos, representação intermediária serializável, interpretador, geração de Python e otimizações locais. A suíte existente do repositório foi executada nesta revisão e aprovou 27 testes. Os resultados sustentam a implementação das regras exercitadas, mas não estimam a confiabilidade para programas arbitrários, a usabilidade por terceiros ou o desempenho.

**Palavras-chave:** compiladores; linguagem específica de domínio; análise semântica; representação intermediária; geração de código.

## 1 Introdução

Regras de jogabilidade como reduzir a vida após uma colisão combinam conceitos simples do domínio com infraestrutura de uma linguagem de propósito geral: objetos, estado, eventos e chamadas auxiliares. Uma linguagem específica de domínio (DSL) pode tornar essas regras mais próximas do vocabulário do problema, desde que seu escopo permaneça delimitado e que a sintaxe não esconda suas consequências de execução [2]. A GameLang foi proposta para estudantes, desenvolvedores iniciantes e criadores independentes que desejam expressar comportamentos básicos sem implementar uma engine completa [5].

O trabalho implementa um compilador educacional observável, do texto-fonte até duas rotas de execução. Além de demonstrar as fases clássicas de um compilador [1, 3], o projeto verifica se nomes, propriedades e operações fazem sentido antes de executar o programa. A contribuição avaliada aqui é a implementação funcional e uma medição delimitada da capacidade do analisador semântico de rejeitar erros intencionais, seguindo a atividade final da disciplina [6].

## 2 Linguagem e decisões de projeto

Um programa GameLang declara entidades com propriedades numéricas, registra eventos e associa instruções ao contato entre entidades. As expressões incluem valores inteiros e reais, texto, booleanos, posições e referências qualificadas como `player.health`. A gramática separa operadores em níveis de precedência; `repeat` oferece repetição e `print` produz saída textual. A seguir, um exemplo completo declara duas entidades, aplica dano em uma colisão e imprime o estado observado.

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

print "arena pronta";
```

A linguagem inclui o tipo domínio posição, representado por um par ordenado numérico, além de valores inteiros, reais, booleanos e texto. As entidades representam objetos do jogo; suas propriedades são resolvidas por nomes qualificados e permanecem num escopo local ao objeto. As expressões definem precedência de unários, multiplicação, adição, comparação, igualdade, conjunção e disjunção. Essa hierarquia torna explícita a interpretação de expressões como `2 + 3 * 4` e oferece conteúdo suficiente para verificar compatibilidade de tipos.

### Tabela 1. Relação entre o escopo obrigatório e as construções implementadas.

| Requisito | Construção da GameLang |
| :--- | :--- |
| **Propósito** | Regras básicas de jogos para estudantes e criadores independentes |
| **Tipo do domínio** | Entidades e posições, além de números |
| **Nomes e escopo** | Entidades globais e propriedades qualificadas |
| **Precedência** | Unários, aritmética, comparação, igualdade e lógica |
| **Controle** | Blocos `repeat` com contagem inteira não negativa |
| **Semântica** | Existência, tipos, `health`, coordenadas e formato de movimento |
| **Saída** | Instrução `print` no runtime |

Três decisões definem o desenho da versão atual.

**Entidades e propriedades qualificadas.** As entidades ficam no escopo global e as propriedades no escopo de cada entidade; a referência `player.health` torna explícito qual estado será lido. Uma tabela plana de variáveis seria mais simples, mas permitiria colisões de nomes e afastaria a representação dos objetos do jogo. A escolha mantém a verificação de existência ligada ao domínio.

**Parser descendente escrito à mão.** A equipe escolheu associatividade à esquerda e funções de parsing por nível de precedência em vez de um gerador de parser. Para a gramática pequena, essa estratégia reduz dependências e permite associar erros ao token corrente; em contrapartida, novas construções exigem manutenção manual das rotinas [1, 3].

**IR estruturada e runtime compartilhado.** Eventos e blocos `repeat` permanecem como estruturas da IR; o projeto não cria CFG ou SSA, pois a versão não possui desvios condicionais. O interpretador e o código Python gerado usam o mesmo runtime, o que reduz a duplicação das regras de estado e facilita comparar os resultados [3, 4]. O custo é que o módulo Python gerado ainda depende de `gamelang.runtime`.

O escopo também deixa de fora funções recursivas, inferência de tipos, módulos e exceções. Essas ausências reduzem a quantidade de mecanismos que a equipe precisou integrar e mantêm as regras de jogo no centro da linguagem. A escolha impõe limites: sem condicionais, os programas descrevem sequências e eventos, não lógica arbitrária de decisão; sem variáveis locais, o estado mutável fica concentrado nas propriedades das entidades.

## 3 Implementação

O lexer percorre a fonte e cria tokens com linha e coluna. O parser descendente produz uma AST imutável e aplica precedência por camadas. A análise semântica registra primeiro entidades e propriedades; depois valida referências, tipos, ações e contagens de repetição. Assim, propriedades inexistentes, dano aplicado a uma entidade sem `health` e movimento sem `x`, `y` ou uma posição numérica são recusados antes da geração de código.

Os valores de propriedades são expressões numéricas constantes, o que torna a inicialização determinística. A semântica distingue inteiro, real, booleano, texto e posição; adição de textos e operações numéricas são aceitas apenas quando compatíveis. As ações usam regras de domínio: `damage` e `heal` requerem `health`, enquanto `move` exige `x`, `y` e um par numérico. `repeat` requer contagem inteira e rejeita constantes negativas. Cada diagnóstico inclui fase, código e posição da origem; na CLI, a mensagem também apresenta arquivo, linha e coluna. A CLI oferece comandos para conferir, imprimir tokens, AST e IR, executar e gerar Python.

A AST validada é convertida em uma IR JSON versionada, que preserva posições de origem. O interpretador executa essa IR em um runtime com estado de entidades, eventos de toque e saída textual. O backend gera Python que chama o mesmo runtime, reduzindo o risco de divergência nas regras de estado entre as duas rotas de execução. O otimizador aplica dobramento de constantes, identidades algébricas, remoção de ações sem efeito e simplificação de `repeat 1`. Os testes comparam snapshots de entidades e saída antes e depois de transformações, bem como entre interpretação e código gerado.

As reescritas são locais e evitam modificar operações cujo resultado depende do estado em execução. No exemplo `04_otimizacoes.gl`, `2 * (3 + 1)` é dobrado para `8`, ações de cura zero e movimento nulo são removidas, e `repeat 1` é substituído pelo corpo. O estado observado permanece `health=32`, `x=5` e `y=2`. Esse caso ilustra preservação funcional; não constitui medição de aceleração. A ferramenta relata contagens por classe de transformação, permitindo inspecionar o efeito antes de interpretar qualquer ganho.

A serialização permite inspecionar e reconstruir a IR, separando parsing, lowering, transformação e execução. O runtime trata colisões como eventos simétricos e recebe os pares de entidades pela CLI, sem tentar simular geometria. A geração para Python mantém o programa visível e facilita a comparação com o interpretador, mas preserva dependência do pacote `gamelang.runtime`. O projeto não usa dependências externas no tempo de execução e documenta instalação opcional do comando `gamelang` no README.

A verificação semântica distingue um programa bem formado de um programa válido no domínio. Por exemplo, depois de declarar `player` com `health`, o comando `damage player by 10;` é aceito. Já `damage ghost by 10;` é sintaticamente válido, mas é rejeitado como entidade inexistente: a mensagem identifica a fase semântica, o código `S005` e a posição do nome. O projeto inclui cinco exemplos inválidos para erros lexicais, sintáticos e semânticos, além de quatro programas válidos.

## 4 Avaliação da verificação semântica

**Pergunta.** A verificação semântica implementada rejeita erros de domínio intencionais sem rejeitar programas corretos? A avaliação segue a opção B do enunciado: entradas inválidas acompanhadas de controles válidos [6].

**Método.** Foram preparados 26 programas sintaticamente válidos com erros semânticos, distribuídos entre seis famílias: declarações duplicadas; propriedades com tipo ou inicialização inválidos; nomes, propriedades e pré-condições de ações; tipos e formatos de ações; contagens de `repeat`; e incompatibilidades entre operadores. Oito programas corretos cobriram declarações, expressões, dano e cura, movimento, repetição, texto e eventos. Cada entrada foi passada a `compile_source`, usando como critério de detecção uma exceção `GameLangError` com fase semântica. Um controle rejeitado contaria como falso positivo; um programa inválido aceito contaria como erro escapado. Os casos individuais estão no Apêndice A.

### Tabela 2. Resultado do corpus semântico construído para esta avaliação.

| Família de erro | Casos | Rejeitados |
| :--- | :---: | :---: |
| Declarações duplicadas | 2 | 2 |
| Tipo e constância de propriedades | 4 | 4 |
| Nomes, propriedades e pré-condições | 7 | 7 |
| Tipos e formato das ações | 5 | 5 |
| Tipo e domínio de repeat | 4 | 4 |
| Compatibilidade de operadores | 4 | 4 |
| **Total** | **26** | **26** |

**Resultados.** O compilador rejeitou 26/26 entradas inválidas (100% de detecção no corpus), sem erros escapados. Aceitou 8/8 controles (0/8 falsos positivos). Todas as 26 rejeições ocorreram na fase semântica e continham linha e coluna. Separadamente, a suíte automatizada já presente no pacote foi executada nesta revisão: 27 testes passaram. A tabela mede o conjunto criado, não a cobertura total da linguagem.

Como verificação complementar, os quatro exemplos válidos foram compilados com otimização, executados pela IR no interpretador e executados como Python gerado. Em cada caso, com os mesmos eventos de toque, os snapshots canônicos de entidades e saída foram idênticos. A Tabela 3 resume os resultados; essa comparação verifica consistência entre rotas para os exemplos incluídos, sem estimar desempenho.

### Tabela 3. Comparação dos estados finais e das saídas em quatro exemplos executados.

| Programa | Snapshot observado | Rotas |
| :--- | :--- | :---: |
| `01_arena` | `player` health=90; `enemy` health=25; 3 saídas | Igual |
| `02_movimento` | `ship` posição=(6,5); saídas 6 e 5 | Igual |
| `03_cura` | `hero` health=50; posição=(3,9); 2 saídas | Igual |
| `04_otimizacoes` | `bot` health=32; posição=(5,2); saídas 32 e 5 | Igual |

A suíte do repositório e o corpus deste artigo têm papéis distintos. Os testes existentes cobrem lexer, parser, precedência, resolução semântica, serialização de IR, execução, equivalência entre interpretador e Python e otimizações. A bateria deste estudo seleciona erros semânticos para medir rejeição e falsos positivos. Os quatro exemplos válidos do pacote compilam; os testes de pipeline também comparam estado e saída em duas rotas de execução.

**Interpretação.** Nos casos construídos, as regras de nomes, tipos, propriedades e ações funcionaram de acordo com o comportamento esperado. A ausência de falsos positivos nos controles indica que as construções válidas selecionadas não foram bloqueadas. O resultado responde à pergunta de verificação para estas famílias e programas; não demonstra que todo erro semântico concebível será detectado.

A taxa observada é descritiva do corpus, sem inferência para uma população de programas. Não há amostragem aleatória: cada caso representa uma condição semântica implementada e foi escolhido deliberadamente. A utilidade do resultado é confirmar que as regras cobertas pela bateria produzem diagnósticos em vez de chegarem ao runtime; a próxima avaliação deve incluir combinações, revisores independentes e programas elaborados por usuários que não conhecem os códigos internos.

## 5 Discussão

A escolha da opção B é compatível com o componente mais distintivo da implementação: decisões semânticas que recusam programas antes da execução. Os casos cobrem regras que correspondem diretamente a códigos S001-S022, como duplicidade, resolução de entidades, propriedades obrigatórias e compatibilidade de expressões. A cobertura não é uniforme por código, mas alcança os grupos que o projeto documenta. A taxa de 26/26 deve ser interpretada como resultado do conjunto deliberadamente construído, não como estimativa de taxa de acerto para código futuro.

Os oito controles dão uma verificação mínima de que as mesmas regras não bloqueiam construções comuns: valores numéricos, posições, repetição, operações de texto e eventos. Um conjunto pequeno não revela combinações raras nem ambiguidades de especificação. Para reduzir viés, uma próxima rodada deve pedir a outra equipe que proponha casos sem consultar os códigos de diagnóstico, registrar previamente o resultado esperado e comparar a avaliação com a execução independente do corpus.

A suíte de 27 testes e a bateria experimental respondem a perguntas diferentes. A suíte verifica componentes e equivalência de execução em cenários escolhidos pelo projeto; o corpus conta rejeições semânticas e controles corretos. Em conjunto, fornecem evidência mais concreta que a descrição isolada da arquitetura, mas ainda não substituem testes de usabilidade, comparação com uma biblioteca Python ou medições por fase. Essas extensões devem ser tratadas como estudos separados, com participantes, tarefas ou instrumentos definidos.

## 6 Limitações e validade

A GameLang não implementa renderização gráfica, áudio, física contínua, entrada de teclado ou detecção geométrica de colisão. Eventos `touches` são informados ao runtime, propriedades iniciais são constantes numéricas e não há condicionais, funções do usuário ou módulos [5]. O backend Python compartilha o runtime da GameLang, portanto o arquivo gerado não é autônomo.

A avaliação tem ameaças claras à validade. Os casos foram criados com conhecimento das regras e dos códigos semânticos, não passaram por rotulagem independente e representam poucas combinações. Oito controles não estimam falsos positivos para programas reais; 26 erros não estimam o comportamento em toda a gramática. Não foram medidos desempenho, facilidade de aprendizagem ou comparação com Python. Os resultados devem ser lidos como teste controlado das regras implementadas, e não como evidência de confiabilidade geral.

Há também limites funcionais relevantes para interpretar a evidência: o evento `touches` só ocorre quando informado pelo usuário, dano pode deixar `health` abaixo de zero, cura não impõe um teto e `repeat` pode consumir recursos com valores grandes. A otimização foi verificada por preservação de estado e saída nos testes fornecidos, sem medir tempo de execução nem afirmar ganho de desempenho. O tamanho do corpus e a ausência de usuários externos impedem conclusões sobre colisões em jogos reais, produtividade ou clareza para iniciantes.

**Reprodução.** O pacote contém o código, os exemplos, o README e a suíte de 27 testes. Execute `python -m unittest discover -s tests -v` na raiz do projeto. Para repetir o corpus do Apêndice A, salve cada programa em um arquivo `.gl` e execute `python -m gamelang check arquivo.gl`; os casos B devem retornar erro semântico e os casos C devem ser aceitos. Repositório da equipe: [https://github.com/joaocosta007/GameLang](https://github.com/joaocosta007/GameLang).

## 7 Conclusão

A GameLang concretiza uma DSL pequena para regras básicas de jogos e um pipeline com análise semântica, IR, interpretação, geração de Python e otimizações. Na bateria controlada desta avaliação, o compilador rejeitou todos os 26 erros semânticos e aceitou os oito controles; a suíte do projeto também passou nos 27 testes. A evidência é positiva para as regras exercitadas, mas ainda limitada por um corpus manual e pequeno. Próximos passos são ampliar e revisar independentemente os casos, executar testes com terceiros e expandir o runtime somente quando a necessidade estiver demonstrada.

## Declaração de uso de inteligência artificial

O registro do projeto informa o uso de Codex baseado em modelo GPT nos testes, no artigo e na apresentação, com revisão humana declarada. Nesta revisão, Codex também apoiou a estruturação e redação deste artigo e preparou e executou o corpus de 26 programas inválidos e oito controles no código fornecido. A equipe deve revisar e reproduzir esses casos e resultados antes da submissão. A responsabilidade pela validação e pela versão final permanece com os autores.

## Apêndice A. Programas da avaliação

Os exemplos abaixo foram submetidos individualmente ao analisador semântico. B01-B26 devem ser rejeitados; C01-C08 são controles válidos. O resultado esperado de cada programa B é indicado pelo código retornado pelo compilador.

| ID | Programa GameLang | Resultado |
| :---: | :--- | :---: |
| **B01** | `entity p { health=1; } entity p { health=2; }` | S001 |
| **B02** | `entity p { health=1; health=2; }` | S002 |
| **B03** | `entity p { health="x"; }` | S003 |
| **B04** | `entity p { health=true; }` | S003 |
| **B05** | `entity q { health=1; } entity p { health=q.health; }` | S004 |
| **B06** | `entity q { health=1; } entity p { health=q.health + 1; }` | S004 |
| **B07** | `damage ghost by 1;` | S005 |
| **B08** | `heal ghost by 1;` | S005 |
| **B09** | `entity p { health=1; } print p.mana;` | S006 |
| **B10** | `entity wall { x=0; y=0; } damage wall by 1;` | S006 |
| **B11** | `entity wall { x=0; y=0; } heal wall by 1;` | S006 |
| **B12** | `entity p { health=1; } damage p by "a";` | S011 |
| **B13** | `entity p { health=1; } heal p by true;` | S011 |
| **B14** | `entity p { health=1; y=0; } move p by (1,2);` | S006 |
| **B15** | `entity p { health=1; x=0; } move p by (1,2);` | S006 |
| **B16** | `entity p { health=1; x=0; y=0; } move p by 1;` | S012 |
| **B17** | `repeat 2.5 { print 1; }` | S013 |
| **B18** | `repeat true { print 1; }` | S013 |
| **B19** | `repeat -1 { print 1; }` | S014 |
| **B20** | `repeat 1 - 3 { print 1; }` | S014 |
| **B21** | `entity p { health=1; x=0; y=0; } move p by ("a",2);` | S020 |
| **B22** | `entity p { health=1; x=0; y=0; } move p by (1,false);` | S020 |
| **B23** | `print -"x";` | S021 |
| **B24** | `print not 3;` | S021 |
| **B25** | `print 1 + true;` | S022 |
| **B26** | `print "a" < "b";` | S022 |
| **C01** | `entity p { health=5; x=0; y=0; } print p.health;` | Aceito |
| **C02** | `entity p { health=5; x=0; y=0; } damage p by 1; heal p by 0.5;` | Aceito |
| **C03** | `entity p { health=5; x=0; y=0; } move p by (1,-2);` | Aceito |
| **C04** | `repeat 0 { print 1; }` | Aceito |
| **C05** | `repeat 2 { print 1; }` | Aceito |
| **C06** | `entity p { health=2.5; x=0.5; y=0; } print p.health + 0.5;` | Aceito |
| **C07** | `print "a" + "b"; print true and not false;` | Aceito |
| **C08** | `entity p { health=5; x=0; y=0; } entity q { health=3; x=1; y=0; } when p touches q { damage p by 1; }` | Aceito |

## Referências

- **[1]** Alfred V. Aho, Monica S. Lam, Ravi Sethi e Jeffrey D. Ullman. 2006. *Compilers: Principles, Techniques, and Tools*. 2. ed. Addison-Wesley.
- **[2]** Martin Fowler com Rebecca Parsons. 2010. *Domain-Specific Languages*. Addison-Wesley Professional.
- **[3]** Keith D. Cooper e Linda Torczon. 2022. *Engineering a Compiler*. 3. ed. Morgan Kaufmann.
- **[4]** Robert Nystrom. 2021. *Crafting Interpreters*. Disponível em [https://craftinginterpreters.com](https://craftinginterpreters.com).
- **[5]** Equipe GameLang. 2026. *GameLang: especificação da linguagem, Entrega 1*. Material de Projeto e Implementação de Compiladores, UNASP-SP.
- **[6]** UNASP-SP. 2026. *Atividade final: criação de uma linguagem de programação e artigo científico*. Projeto e Implementação de Compiladores, semestre 2026/2.
