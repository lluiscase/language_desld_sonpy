# Linguagem Narrativa: análise do código do Gemini e versão melhorada

Origem: conversa compartilhada do Gemini (11 turnos) em que foi construída uma
linguagem de programação "em forma de história" em Python.

```
linguagem_narrativa/
├── original_gemini/          # código da conversa, extraído sem alterações
│   ├── conversa_gemini.md    # conversa completa (perguntas + respostas)
│   ├── interpretador.py      # turno 10: versão final em arquivo único
│   ├── meu_interpretador/    # turnos 6-9: pacote pip (historia/core.py, cli.py, pyproject.toml)
│   ├── versoes_intermediarias/  # turnos 0-5: v0_basico ... v5_dialogos
│   ├── CONTEXTO_PROJETO_LANG_NARRATIVA.md   # turno 8
│   └── PROMPT_CRIACAO_PROJETO.md           # turno 9
└── melhorado/                # nova implementação com o pipeline completo de compilação
    ├── narrativa/            # lexer, parser, AST, semântica, interpretador, gerador, runtime, CLI
    ├── exemplos/             # conto.hist, feira.hist, erro.hist
    └── README.md             # manual da linguagem + gramática
```

## 1. O código original tem as fases de um compilador?

**Não.** A conversa diz que existem 3 etapas (lexer, parser, interpretador), mas o
código não as implementa. Cada linha é testada contra uma sequência de expressões
regulares (`re.match`), e a primeira que casar já executa a ação. É um
*casador de padrões linha a linha*, não um compilador.

| Fase | Original (Gemini) | Melhorado |
| --- | --- | --- |
| Análise léxica (tokens) | ❌ não existe; o texto bruto vai direto para o regex | ✅ `lexer.py`: tokens com tipo, linha e coluna |
| Análise sintática (gramática → árvore) | ❌ não existe; não há gramática nem AST | ✅ `parser.py`: parser descendente recursivo → AST (`nos.py`) |
| Análise semântica | ❌ não existe | ✅ `semantica.py`: tipos, capítulos, avisos de laço infinito e de variável sem valor |
| Execução | ⚠️ executa durante o "parse", linha por linha | ✅ `interpretador.py` percorre a AST |
| Geração de código | ❌ não existe | ✅ `gerador.py`: gera um programa Python independente |
| Mensagens de erro | ❌ linha desconhecida vira `[Instrução]` e é ignorada | ✅ erro com fase, linha, coluna e trecho marcado |
| Blocos aninhados | ❌ impossível (o bloco é "tudo até o 1º `Fim do laço`") | ✅ qualquer profundidade |

## 2. Bugs encontrados no original

**Exemplos em que o Gemini mostrou uma saída que o código não produz:**

1. **Turno 10 (versão final) e turno 5:** `{joao.maçã}` sai como `[joao.maçã desconhecido]`,
   porque a chave guardada é `joão.maçã`. O próprio exemplo final do Gemini imprime isso.
2. **Turno 3:** `Enquanto Maria tiver maçãs ela dá 1 maçã para João` **nunca executa**. O regex
   não guloso captura só `Maria` como condição. O Gemini mostrou "Executado 5 vez(es)".
3. **Turno 1:** `Maria tem mais maçãs do que 50?` devolve "Não foi possível comparar".
   O Gemini mostrou "É Verdadeiro".

**Recursos que existiam e sumiram na versão final:**

4. `Se ... então` é ignorado.
5. `multiplica por` / `divide por` são ignorados.
6. Condições `mais de` / `menos de` são sempre falsas.

**Robustez:**

7. Erro de digitação (`Maria tme 3 maçãs`) é aceito em silêncio.
8. `mora em` e `é` gravam na mesma chave `atributo`, e um apaga o outro.
9. `Mostre Maria` mostra todo mundo.
10. Sem `Fim do laço` (ou escrito `Fim do laco`), o resto da história vira corpo do laço.
11. Um erro dentro de um laço gera mil mensagens até o limite.
12. Laços aninhados não funcionam.
13. `rstrip('s')` tira todos os "s" do fim: `lápis` → `lápi`.
14. `perde` mais do que tem zera sem avisar.

## 3. Melhorias

**Arquitetura de compilador:** lexer → parser → AST → semântica → interpretador **ou** gerador de
Python. O `runtime.py` é compartilhado pelos dois caminhos, então o código compilado e o interpretado
se comportam igual.

**Linguagem:**
* Os recursos perdidos voltaram: `Se/então/senão`, `multiplica`, `divide`, comparações.
* Novos: `Senão se`, `e`/`ou`/`não`, perguntas (`... ?`), `Repita N vezes`,
  capítulos (funções, inclusive recursivas), `dá todas as`, números por extenso,
  listas (`tem 3 maçãs, 2 peras e 1 banana`), narrador, mais verbos sinônimos.
* O exemplo do pedido inicial, `Maria tem 40 maças, maça vezes 2`, agora funciona
  e dá 80. A versão final do Gemini não aceitava essa frase.
* Nomes e itens são normalizados (acentos, maiúsculas, plural/singular em português).
* Pronomes: `para ela` aponta para o outro personagem, não para quem está dando.

**Ferramentas:** `--trace`, `compilar`, `verificar`, `tokens`, `ast`, `repl`, erros com linha e
coluna, limite de laço configurável, sem dependências externas.

## Limitações conhecidas

* Só inteiros não negativos (`dividido por` é divisão inteira).
* Os pronomes não consideram gênero: `ela` é o personagem citado mais recentemente.
* O singular é feito por regras simples. Plurais irregulares raros podem não casar.
# language_desld_sonpy
