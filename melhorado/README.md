# Linguagem Narrativa 0.2

Uma linguagem de programação em português que se escreve como uma história.

```text
Maria tem 3 maçãs.
João tem 0 maçãs e 0 moedas.

Enquanto Maria tiver maçãs faça:
    Maria dá 1 maçã para João.
    João ganha 2 moedas.
Fim do laço.

João diz: "Agora eu tenho {joão.maçãs} maçãs e {joão.moedas} moedas."
```

```
🗣️  João diz: "Agora eu tenho 3 maçãs e 6 moedas."
```

## Instalação e uso

Requer Python 3.9 ou mais novo. Não tem dependências.

```bash
pip install -e .                                # instala os comandos `narrativa` e `historia`
narrativa executar exemplos/conto.hist          # roda a história
narrativa executar --trace exemplos/conto.hist  # mostra a memória a cada passo
narrativa compilar exemplos/conto.hist          # gera exemplos/conto.py (Python puro)
narrativa verificar exemplos/feira.hist         # só checa erros e avisos
narrativa tokens exemplos/conto.hist            # saída do analisador léxico
narrativa ast exemplos/conto.hist               # árvore sintática
narrativa repl                                  # modo interativo
```

Sem instalar: `python -m narrativa executar exemplos/conto.hist` (de dentro desta pasta).

## Como o compilador funciona

```
história (.hist)
   │  lexer.py        Fase 1 - análise léxica: texto -> tokens (com linha e coluna)
   ▼
tokens
   │  parser.py       Fase 2 - análise sintática: tokens -> AST (parser descendente recursivo)
   ▼
AST (nos.py)
   │  semantica.py    Fase 3 - análise semântica: tipos, capítulos, avisos de laço infinito...
   ▼
AST verificada ─────────────┬──────────────────────────────┐
   │  interpretador.py      │  gerador.py                  │
   ▼  Fase 4a - executa     ▼  Fase 4b - gera código Python │
saída                    programa .py independente         │
                                                            │
       runtime.py: memória e operações, usado pelos dois caminhos
```

O `runtime.py` é copiado para dentro do `.py` gerado. Por isso o interpretador
e o código compilado têm exatamente o mesmo comportamento.

## A linguagem

Nomes não diferenciam maiúsculas nem acentos, e itens não diferenciam
singular de plural: `João`, `joao`, `JOÃO` são a mesma pessoa, e
`maçãs`, `maçã`, `maças` são o mesmo item. Frases terminam com `.`, `!`, `;` ou
quebra de linha. `#` começa um comentário. Números podem vir por extenso (`três`, `uma`).

| O que | Como se escreve |
| --- | --- |
| Criar quantidade | `Maria tem 40 maçãs.` · `João tem 3 maçãs, 2 peras e uma banana.` |
| Somar / subtrair | `Maria ganha 10 maçãs.` (recebe, compra, colhe) · `Maria perde 5 maçãs.` (gasta, come, vende) · `Maria perde todas as maçãs.` |
| Multiplicar / dividir | `Maria multiplica por 2 suas maçãs.` · `Maria divide suas maçãs por 3.` · `Maria dobra suas maçãs.` · `Maria triplica suas maçãs.` |
| Operar no último personagem citado | `Maria tem 40 maçãs, maçã vezes 2.` (também `mais`, `menos`, `dividido por`) |
| Transferir | `Maria dá 1 maçã para João.` (entrega, passa, empresta) · `Maria dá todas as maçãs para João.` |
| Texto | `Maria mora em "Recife".` (cidade) · `Maria é "Feliz".` (status) · `Maria se chama "Mari".` (nome) · `Maria está em "casa".` (local) · `O apelido de Maria é "Mari".` (qualquer atributo) |
| Falar | `Maria diz: "Tenho {maria.maçãs} maçãs."` (fala, pergunta, responde, grita, sussurra, pensa) |
| Narrar | `Narrador: "Era uma vez..."` ou só `"Era uma vez..."` |
| Mostrar memória | `Mostre tudo.` · `Mostre Maria.` |
| Pergunta | `Maria tem mais maçãs do que João?` → `❓ ... Sim` |
| Pronomes | `ela` / `ele` = último personagem citado. Depois de `para`, é o último citado que não seja quem dá |
| Se | `Se <condição> então <frase>[, senão <frase>].` ou em bloco, com `Senão se ... então:` / `Senão:` e fechando com `Fim do se.` |
| Enquanto | `Enquanto <condição> <frase>.` ou `Enquanto <condição> faça:` ... `Fim do laço.` |
| Repita | `Repita 3 vezes: <frase>.` ou em bloco, fechando com `Fim da repetição.` |
| Capítulo (função) | `Capítulo Colheita:` ... `Fim do capítulo.` e depois `Conte o capítulo Colheita.` |

Várias frases numa mesma linha de `Se`/`Enquanto`/`Repita` são ligadas por `e`:
`Se Ana tiver peras então ela dá 1 pera para Bia e Bia ganha 1 moeda.`

### Condições

| Forma | Significa |
| --- | --- |
| `Maria tiver maçãs` | maçãs > 0 |
| `Maria tiver 5 maçãs` / `pelo menos 5` | >= 5 |
| `mais de 5` / `menos de 5` / `no máximo 5` / `exatamente 5` | > / < / <= / == |
| `Maria tiver nenhuma maçã` / `Maria não tiver maçãs` | == 0 / não (> 0) |
| `Maria tiver mais maçãs que João` / `menos ... do que` / `tantas ... quanto` | compara dois personagens (ou um número) |
| `Maria mora em "Recife"` / `Maria é "Feliz"` | compara texto (sem diferenciar maiúsculas) |
| `<cond> e <cond>`, `<cond> ou <cond>` | `e` tem precedência sobre `ou` |

### Gramática (EBNF simplificada)

```ebnf
programa     = { instrucao } ;
instrucao    = se | enquanto | repita | capitulo | frases , fim_frase ;
frases       = frase , { "e" , frase } ;
frase        = mostre | chamada | narracao | atributo_de | pergunta | op_implicita
             | sujeito , ( ter | ganhar | perder | mult_div | dar | falar | texto_attr ) ;
ter          = ("tem"|"possui") , lista_qtd ;
lista_qtd    = qtd , item , { ("," | "e") , qtd , item } ;
dar          = VERBO_DAR , qtd_ou_todas , item , ("para"|"a"|"ao") , sujeito ;
falar        = VERBO_FALA , [":"] , TEXTO ;
se           = "Se" , condicao , ("então" , frases , [ [","] "senão" , frases ] , fim_frase
                                  | ["então"] , ":" , NL , bloco , [senao] , "Fim" ...) ;
senao        = "Senão" , ( "se" , condicao , ["então"] , ":" , NL , bloco , [senao]
                         | ":" , NL , bloco ) ;
enquanto     = "Enquanto" , condicao , ["faça"] , ( frases , fim_frase | ":" , NL , bloco , "Fim" ... ) ;
repita       = "Repita" , qtd , "vezes" , ( [":"] frases , fim_frase | ":" , NL , bloco , "Fim" ... ) ;
capitulo     = "Capítulo" , nome , ":" , NL , bloco , "Fim" ... ;
condicao     = cond_e , { "ou" , cond_e } ;
cond_e       = cond_simples , { "e" , cond_simples } ;
cond_simples = sujeito , ["não"] , ( ("tiver"|"tem") , comparacao | verbo_texto , TEXTO ) ;
pergunta     = condicao , "?" ;
item         = PALAVRA , { PALAVRA } ;   (* termina em para, que, do, e, ou, então, faça, ela... *)
```

## Erros com linha e coluna

```
Erro de sintaxe na linha 5, coluna 1: Esperava 'Fim do laço' para fechar o bloco da linha 3, mas encontrei 'Fim do se'
   5 | Fim do se.
     | ^
```

| Fase | Exemplos |
| --- | --- |
| Léxico | texto sem aspas de fechamento, caractere inválido |
| Sintaxe | verbo desconhecido (erro de digitação), bloco sem `Fim`, `Fim` do tipo errado, pronome sem antecedente, `{referência}` inválida |
| Semântica (erro) | capítulo inexistente ou duplicado, item usado como texto e como número, divisão por 0 |
| Semântica (aviso) | item usado sem valor, `Enquanto` cujo corpo não muda a condição, capítulo nunca usado |
| Execução | dar/perder mais do que tem, `{maria.peras}` inexistente, laço passou do limite (padrão 10.000, `--limite-laco`), capítulo que chama a si mesmo sem fim |

## Diferenças em relação à versão do Gemini

* Atributos de texto têm nome próprio (`{maria.cidade}`, `{maria.status}`) em vez de
  uma única chave `{maria.atributo}`, onde um texto apagava o outro.
* Por padrão só aparece a saída da história (falas, narração, `Mostre`, perguntas).
  O log de cada passo virou a opção `--trace`.
* Frases não reconhecidas são **erro de sintaxe**. Antes eram ignoradas em silêncio.
* Dar ou perder mais do que se tem é **erro**. Antes virava 0 sem aviso, ou mil mensagens repetidas dentro de um laço.
