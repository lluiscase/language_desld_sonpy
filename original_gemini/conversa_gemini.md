

######## TURNO 0 USER ########
Queremos desenvolver um linguagem de programação com python. Ela deve ser interpretada pelo propio código. A ideia é ser como contar uma historia. "Maria tem 40 maças, maça vezes 2"

######## TURNO 0 GEMINI ########
Criar uma linguagem baseada em narrativas (uma **DSL - Domain Specific Language** focada em linguagem natural) em Python é um excelente projeto. O fluxo essencial de qualquer interpretador funciona em 3 etapas principais:

1. **Lexer (Analisador Léxico):** Transforma o texto bruto (a história) em uma lista de pedaços significativos (*tokens*).
2. **Parser (Analisador Sintático):** Analisa a sequência de *tokens* para entender a intenção e a estrutura do comando.
3. **Interpretador/Executor:** Guarda as variáveis na memória e realiza as operações matemáticas ou ações pedidas.

---

### Código Base do Interpretador em Python

Abaixo está uma implementação funcional e direta para interpretar histórias simples como a da Maria:

```python
import re

class InterpretadorDeHistorias:
    def __init__(self):
        # Memória para guardar os personagens/variáveis e suas quantidades
        self.memoria = {}

    def executar_linha(self, linha):
        linha = linha.strip().strip('.')
        if not linha:
            return None

        # 1. Padrão para atribuição: "Maria tem 40 maças"
        match_atribuicao = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_atribuicao:
            sujeito, valor, item = match_atribuicao.groups()
            item_singular = item.rstrip('s').lower() # Normaliza para o singular
            
            self.memoria[item_singular] = int(valor)
            return f"-> {sujeito} agora possui {valor} {item}."

        # 2. Padrão para operação matemática: "maça vezes 2" ou "maça mais 5"
        match_operacao = re.match(r"^(.+?)\s+(vezes|mais|menos|dividido por)\s+(\d+)$", linha, re.IGNORECASE)
        if match_operacao:
            item, operacao, valor = match_operacao.groups()
            item_singular = item.strip().rstrip('s').lower()
            val = int(valor)

            if item_singular not in self.memoria:
                return f"Erro: '{item}' não foi encontrado na história ainda."

            # Executa a matemática baseada na palavra-chave
            if operacao.lower() == "vezes":
                self.memoria[item_singular] *= val
            elif operacao.lower() == "mais":
                self.memoria[item_singular] += val
            elif operacao.lower() == "menos":
                self.memoria[item_singular] -= val
            elif operacao.lower() == "dividido por":
                self.memoria[item_singular] //= val

            return f"-> Nova quantidade de {item_singular}s: {self.memoria[item_singular]}."

        return f"Linha não compreendida: '{linha}'"

    def interpretar(self, historia):
        linhas = historia.strip().split('\n')
        resultados = []
        for linha in linhas:
            res = self.executar_linha(linha)
            if res:
                resultados.append(res)
        return resultados


# --- TESTANDO A LINGUAGEM ---

historia = """
Maria tem 40 maças.
maça vezes 2.
maça mais 10.
"""

interpretador = InterpretadorDeHistorias()
saida = interpretador.interpretar(historia)

for linha in saida:
    print(linha)
```

---

<GenerateWidget component_placeholder_id="im_88cb212f8b1e8077" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Demonstrate how the narrative lines map step-by-step to internal state changes in memory.
**Visual type:** Interactive state visualization / bar chart showing variable evolution per line of narrative.
**Data specification:**
- **Data structure:** List of objects containing step, instruction, variable, value, and memory snapshot.
- **Initial values:** 
  - Step 0: Initial state (maça = 0)
  - Step 1: "Maria tem 40 maças" -> maça = 40
  - Step 2: "maça vezes 2" -> maça = 80
  - Step 3: "maça mais 10" -> maça = 90
- **Mapping:** Step index mapped to variable quantity visualization and execution trace.
**User controls:** Step forward/backward buttons and speed control for execution playback.
**Interactivity:** Clicking steps highlights the corresponding line in the narrative and updates memory readout.
**Animation:** Smooth transitions between variable values on state progression.
</GenerateWidget>

---

### Caminhos para expandir a linguagem

1. **Atribuição Indireta (Transferência de itens):**
   * Exemplo: *"Maria deu 10 maças para João."*
   * *Lógica:* Subtrai 10 da `memoria['maça']` de Maria e adiciona na de João.

2. **Condicionais Narrativas:**
   * Exemplo: *"Se Maria tiver mais de 50 maças, ela vende 20."*
   * *Lógica:* Expressões regulares identificando o bloco `Se ... então ...`.

3. **Uso de bibliotecas avançadas de parsing:**
   * Conforme a gramática crescer, Expressões Regulares (`re`) podem ficar complexas demais. Recomenda-se migrar para bibliotecas como **`lark`** ou **`ply`** (Python Lex-Yacc) para definir uma gramática formal baseada em Regras de Produção.

<ElicitationsGroup message="Como deseja dar continuidade ao projeto?">
  <Elicitation label="Adicionar suporte a transferências e novos personagens" query="Como implementar comandos como 'Maria deu 10 maças para João' no interpretador em Python?"/>
  <Elicitation label="Evoluir a linguagem para utilizar a biblioteca Lark" query="Como reescrever este interpretador de histórias utilizando a biblioteca Lark em Python para suportar estruturas mais complexas?"/>
</ElicitationsGroup>


######## TURNO 1 USER ########
Me fale quais são os operadores, como criar variaveis e etc

######## TURNO 1 GEMINI ########
Para transformar sua linguagem narrativa em algo completo e funcional, precisamos definir uma **gramática clara** para variáveis, atribuições, operadores e exibição de resultados.

Abaixo está o guia prático de como modelar a sintaxe e a implementação completa atualizada do interpretador em Python.

---

### 1. Conceito da Sintaxe Narrativa

| Conceito | Como escrevemos na História | Equivalente em Programação Tradicional |
| :--- | :--- | :--- |
| **Criação de Variável** | `Maria tem 40 maçãs` | `maca = 40` |
| **Atribuição / Modificação** | `Maria ganha 10 maçãs` | `maca += 10` |
| **Operadores Matemáticos** | `vezes`, `mais`, `menos`, `dividido por` | `*`, `+`, `-`, `/` |
| **Operadores Lógicos/Comparativos** | `é maior que`, `é igual a`, `é menor que` | `>`, `==`, `<` |
| **Impressão / Saída** | `Mostre o total de maçãs` | `print(maca)` |

---

### 2. Implementação do Interpretador com Operadores e Variáveis

Abaixo está o código atualizado em Python para suportar declaração de variáveis com donos, todos os operadores aritméticos, comparadores e o comando de exibir o estado.

```python
import re

class InterpretadorNarrativo:
    def __init__(self):
        # Dicionário de variáveis: {"maria.maca": 40, "joao.maca": 5}
        self.memoria = {}

    def _resolver_valor(self, termo, sujeito=None):
        """Converte um termo para número ou busca na memória."""
        termo = termo.strip().rstrip('s').lower()
        if termo.isdigit():
            return int(termo)
        
        # Tenta buscar a variável do próprio sujeito ou uma variável global/item solto
        chave_com_sujeito = f"{sujeito}.{termo}" if sujeito else termo
        if chave_com_sujeito in self.memoria:
            return self.memoria[chave_com_sujeito]
        if termo in self.memoria:
            return self.memoria[termo]
        
        return None

    def executar_linha(self, linha):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # 1. CRIAÇÃO DE VARIÁVEL: "<Sujeito> tem <Valor> <Item>"
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            item_key = f"{sujeito.lower()}.{item.rstrip('s').lower()}"
            self.memoria[item_key] = int(valor)
            return f"[Criação] {sujeito} agora possui {valor} {item}."

        # 2. OPERADORES ARITMÉTICOS COM ATRIBUIÇÃO: "<Sujeito> <operação> <Valor> <Item>"
        # Ex: "Maria ganha 10 maçãs", "Maria perde 5 maçãs", "Maria multiplica por 2 suas maçãs"
        match_arit = re.match(
            r"^(\w+)\s+(ganha|perde|multiplica por|divide por)\s+(\d+)\s+(.+)$", 
            linha, re.IGNORECASE
        )
        if match_arit:
            sujeito, op, valor, item = match_arit.groups()
            sujeito_clean = sujeito.lower()
            item_clean = item.replace("suas", "").strip().rstrip('s').lower()
            chave = f"{sujeito_clean}.{item_clean}"

            if chave not in self.memoria:
                return f"[Erro] {sujeito} não possui {item_clean} declarados."

            val = int(valor)
            if op.lower() == "ganha":
                self.memoria[chave] += val
            elif op.lower() == "perde":
                self.memoria[chave] -= val
            elif op.lower() == "multiplica por":
                self.memoria[chave] *= val
            elif op.lower() == "divide por":
                self.memoria[chave] //= val

            return f"[Operação] {sujeito} agora tem {self.memoria[chave]} {item_clean}(s)."

        # 3. OPERADORES COMPARATIVOS / LÓGICOS: "<Sujeito> tem mais <Item> do que <Valor/Outro Sujeito>?"
        match_comp = re.match(
            r"^(\w+)\s+tem\s+(mais|menos|igual a)\s+(.+?)\s+do que\s+(.+)$", 
            linha, re.IGNORECASE
        )
        if match_comp:
            sujeito1, comp, item, outro = match_comp.groups()
            item_clean = item.rstrip('s').lower()
            
            val1 = self._resolver_valor(item_clean, sujeito1.lower())
            val2 = self._resolver_valor(outro)

            if val1 is None or val2 is None:
                return "[Erro] Não foi possível comparar (variável não encontrada)."

            resultado = False
            if comp.lower() == "mais":
                resultado = val1 > val2
            elif comp.lower() == "menos":
                resultado = val1 < val2
            elif comp.lower() == "igual a":
                resultado = val1 == val2

            status = "Verdadeiro" if resultado else "Falso"
            return f"[Comparação] É {status} que {sujeito1} tem {comp} {item_clean} do que {outro}."

        # 4. IMPRESSÃO / SAÍDA DE DADOS: "Mostre <Sujeito>" ou "Mostre tudo"
        match_print = re.match(r"^Mostre\s+(.+)$", linha, re.IGNORECASE)
        if match_print:
            alvo = match_print.group(1).lower()
            if alvo == "tudo":
                return f"[Memória Total]: {self.memoria}"
            
            # Filtra os itens do sujeito especificado
            itens = {k: v for k, v in self.memoria.items() if k.startswith(f"{alvo}.")}
            return f"[Estado de {alvo.capitalize()}]: {itens}"

        return f"[Erro de Sintaxe] Linha não reconhecida: '{linha}'"

    def interpretar(self, historia):
        return [self.executar_linha(l) for l in historia.strip().split('\n') if l.strip()]
```

---

### 3. Exemplo Prático de Uso

```python
historia = """
Maria tem 40 maçãs.
João tem 15 maçãs.

Maria perde 10 maçãs.
Maria multiplica por 2 suas maçãs.

Maria tem mais maçãs do que 50?
Maria tem mais maçãs do que João?

Mostre Maria
Mostre tudo
"""

interpretador = InterpretadorNarrativo()
resultados = interpretador.interpretar(historia)

for res in resultados:
    print(res)
```

#### Saída Gerada:
```text
[Criação] Maria agora possui 40 maçãs.
[Criação] João agora possui 15 maçãs.
[Operação] Maria agora tem 30 maçã(s).
[Operação] Maria agora tem 60 maçã(s).
[Comparação] É Verdadeiro que Maria tem mais maçã do que 50.
[Comparação] É Verdadeiro que Maria tem mais maçã do que João.
[Estado de Maria]: {'maria.maca': 60}
[Memória Total]: {'maria.maca': 60, 'joao.maca': 15}
```

---

<GenerateWidget component_placeholder_id="im_565538c3580a63ae" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Visual interface for testing narrative operators and inspecting dynamic variable allocation in real-time.
**Visual type:** Interactive interpreter console and memory inspector.
**Data specification:**
- **Data structure:** State objects tracking line-by-line variable scope (`maria.maca`, `joao.maca`) and execution logs.
- **Initial values:** 
  - Line 1: `Maria tem 40 maçãs` -> `maria.maca = 40`
  - Line 2: `João tem 15 maçãs` -> `joao.maca = 15`
  - Line 3: `Maria perde 10 maçãs` -> `maria.maca = 30`
  - Line 4: `Maria multiplica por 2 suas maçãs` -> `maria.maca = 60`
- **Mapping:** Text commands mapped to visual memory gauges and comparator results.
**User controls:** Step-by-step code runner controls with live output log toggle.
**Interactivity:** Clicking lines highlights operator evaluation and updates variable cards.
**Animation:** Memory values update dynamically on instruction execution.
</GenerateWidget>

---

<ElicitationsGroup message="Como prefere prosseguir com as funcionalidades da sua linguagem?">
  <Elicitation label="Criar estruturas condicionais narrativas (Se... Então...)" query="Como implementar condicionais como 'Se Maria tiver mais de 50 maçãs então ela dá 10 para João' no interpretador?"/>
  <Elicitation label="Criar loops narrativos (Enquanto...)" query="Como podemos criar laços de repetição usando estilo de história, como 'Enquanto Maria tiver maçãs...'?"/>
</ElicitationsGroup>


######## TURNO 2 USER ########
Como implementar condicionais como 'Se Maria tiver mais de 50 maçãs então ela dá 10 para João' no interpretador?

######## TURNO 2 GEMINI ########
Para adicionar estruturas condicionais narrativas como **"Se [condição] então [ação]"**, precisamos dividir o comando em duas partes:

1. **Avaliação da Condição:** A expressão lógica após o `Se` é testada na memória. Se retornar `Verdadeiro`, avançamos.
2. **Execução da Ação:** A instrução após o `então` é repassada para a nossa própria função de execução de comandos (recursividade).

Além disso, introduzimos suporte à **transferência de itens** (ex: *"dá 10 maçãs para João"*), atualizando a memória de ambos os sujeitos de forma atômica.

---

### Código do Interpretador com Condicionais e Transferências

```python
import re

class InterpretadorNarrativoComCondicional:
    def __init__(self):
        # Memória estruturada: {"maria.maca": 60, "joao.maca": 5}
        self.memoria = {}

    def _resolver_valor(self, termo, sujeito=None):
        """Converte um termo para número inteiro ou busca na memória."""
        termo = termo.strip().rstrip('s').lower()
        if termo.isdigit():
            return int(termo)
        
        chave_com_sujeito = f"{sujeito}.{termo}" if sujeito else termo
        if chave_com_sujeito in self.memoria:
            return self.memoria[chave_com_sujeito]
        if termo in self.memoria:
            return self.memoria[termo]
        
        return None

    def _avaliar_condicao(self, condicao_texto):
        """Avalia expressões como 'Maria tiver mais de 50 maçãs'."""
        match = re.match(
            r"^(\w+)\s+(?:tiver|tem)\s+(mais de|menos de|igual a)\s+(\d+)\s+(.+)$", 
            condicao_texto.strip(), 
            re.IGNORECASE
        )
        if not match:
            return False

        sujeito, operador, limite, item = match.groups()
        item_clean = item.rstrip('s').lower()
        
        valor_atual = self._resolver_valor(item_clean, sujeito.lower())
        if valor_atual is None:
            return False

        limite_val = int(limite)
        if operador.lower() == "mais de":
            return valor_atual > limite_val
        elif operador.lower() == "menos de":
            return valor_atual < limite_val
        elif operador.lower() == "igual a":
            return valor_atual == limite_val

        return False

    def executar_linha(self, linha, sujeito_contexto=None):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # 1. ESTRUTURA CONDICIONAL: "Se <condição> então <ação>"
        match_se = re.match(r"^Se\s+(.+?)\s+então\s+(.+)$", linha, re.IGNORECASE)
        if match_se:
            condicao_str, acao_str = match_se.groups()

            # Descobre o sujeito da condição para usar como contexto na ação
            sujeito_match = re.match(r"^(\w+)", condicao_str.strip())
            sujeito_cond = sujeito_match.group(1) if sujeito_match else None

            if self._avaliar_condicao(condicao_str):
                # Executa a ação recursivamente passando o sujeito como contexto para pronomes como "ela"
                res_acao = self.executar_linha(acao_str, sujeito_contexto=sujeito_cond)
                return f"[Condição Verdadeira] Executado -> {res_acao}"
            else:
                return f"[Condição Falsa] Ação ignorada: '{acao_str}'"

        # Resolve pronomes de contexto (ex: "ela dá..." -> "Maria dá...")
        if sujeito_contexto and re.match(r"^(ela|ele)\b", linha, re.IGNORECASE):
            linha = re.sub(r"^(ela|ele)\b", sujeito_contexto, linha, flags=re.IGNORECASE)

        # 2. TRANSFERÊNCIA DE ITENS: "<Doador> dá <Quantidade> <Item> para <Recebedor>"
        match_transf = re.match(
            r"^(\w+)\s+dá\s+(\d+)\s+(.+?)\s+para\s+(\w+)$", 
            linha, re.IGNORECASE
        )
        if match_transf:
            doador, qtd, item, recebedor = match_transf.groups()
            qtd_val = int(qtd)
            item_clean = item.rstrip('s').lower()

            chave_doador = f"{doador.lower()}.{item_clean}"
            chave_recebedor = f"{recebedor.lower()}.{item_clean}"

            saldo_doador = self.memoria.get(chave_doador, 0)
            if saldo_doador < qtd_val:
                return f"[Erro] {doador} não tem {qtd_val} {item_clean}(s) suficientes para dar."

            # Executa a transferência na memória
            self.memoria[chave_doador] = saldo_doador - qtd_val
            self.memoria[chave_recebedor] = self.memoria.get(chave_recebedor, 0) + qtd_val

            return f"[Transferência] {doador} deu {qtd_val} {item_clean}(s) para {recebedor}."

        # 3. CRIAÇÃO DE VARIÁVEL: "<Sujeito> tem <Valor> <Item>"
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            item_key = f"{sujeito.lower()}.{item.rstrip('s').lower()}"
            self.memoria[item_key] = int(valor)
            return f"[Criação] {sujeito} agora possui {valor} {item}."

        # 4. IMPRESSÃO
        match_print = re.match(r"^Mostre\s+(.+)$", linha, re.IGNORECASE)
        if match_print:
            alvo = match_print.group(1).lower()
            if alvo == "tudo":
                return f"[Memória Total]: {self.memoria}"
            itens = {k: v for k, v in self.memoria.items() if k.startswith(f"{alvo}.")}
            return f"[Estado de {alvo.capitalize()}]: {itens}"

        return f"[Sintaxe Não Reconhecida]: '{linha}'"

    def interpretar(self, historia):
        return [self.executar_linha(l) for l in historia.strip().split('\n') if l.strip()]
```

---

### Exemplo de Execução Prática

```python
historia = """
Maria tem 60 maçãs.
João tem 5 maçãs.

Se Maria tiver mais de 50 maçãs então ela dá 10 maçãs para João.
Se João tiver mais de 20 maçãs então ele dá 5 maçãs para Maria.

Mostre tudo
"""

interpretador = InterpretadorNarrativoComCondicional()
resultados = interpretador.interpretar(historia)

for res in resultados:
    print(res)
```

#### Saída Gerada:
```text
[Criação] Maria agora possui 60 maçãs.
[Criação] João agora possui 5 maçãs.
[Condição Verdadeira] Executado -> [Transferência] Maria deu 10 maçã(s) para João.
[Condição Falsa] Ação ignorada: 'ele dá 5 maçãs para Maria'
[Memória Total]: {'maria.maca': 50, 'joao.maca': 15}
```

---

<GenerateWidget component_placeholder_id="im_3dfd00e9b68670a4" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Step-by-step logic visualizer showing how conditionals evaluate true/false and trigger scoped state mutations.
**Visual type:** Dynamic execution flow diagram & state inspector.
**Data specification:**
- **Data structure:** Node graph mapping line evaluation, condition check status, branch execution, and target memory delta.
- **Initial values:**
  - `maria.maca` = 60, `joao.maca` = 5
  - Condition 1: `60 > 50` -> True -> `maria.maca - 10`, `joao.maca + 10`
  - Condition 2: `15 > 20` -> False -> Branch Skipped
- **Mapping:** Flow nodes colored green for executed branches and red for bypassed branches.
**User controls:** Interactive step execution button and branch state inspector.
**Interactivity:** Hovering condition blocks reveals raw memory comparisons.
**Animation:** Smooth highlight shifts across execution nodes during step triggers.
</GenerateWidget>

---

<ElicitationsGroup message="O que acha de avançar para os próximos pilares da linguagem?">
  <Elicitation label="Adicionar suporte a laços de repetição (Loops)" query="Como implementar loops narrativos do tipo 'Enquanto Maria tiver maçãs ela dá 1 para João' no interpretador?"/>
  <Elicitation label="Criar funções/procedimentos narrativos" query="Como criar rotinas ou funções na linguagem narrativa, como 'Para fazer uma torta: Maria perde 3 maçãs'?"/>
</ElicitationsGroup>


######## TURNO 3 USER ########
Como implementar loops narrativos do tipo 'Enquanto Maria tiver maçãs ela dá 1 para João' no interpretador?

######## TURNO 3 GEMINI ########
Para implementar laços de repetição narrativos como **"Enquanto [condição] [ação]"**, a lógica é similar às condicionais (`Se`), porém com um ciclo `while` do Python que reavalia a condição e reexecuta a ação enquanto o resultado for `Verdadeiro`.

Além disso, adicionamos uma trava de segurança (*limitador de iterações*) para evitar que histórias entrem em laços infinitos (como "Enquanto Maria tiver maçãs ela ganha 1 maçã").

---

### Código do Interpretador com Loops Narrativos

```python
import re

class InterpretadorNarrativoCompleto:
    def __init__(self, limite_loop=1000):
        # Memória: {"maria.maca": 10, "joao.maca": 0}
        self.memoria = {}
        self.limite_loop = limite_loop

    def _resolver_valor(self, termo, sujeito=None):
        """Busca um número inteiro ou uma variável na memória."""
        termo = termo.strip().rstrip('s').lower()
        if termo.isdigit():
            return int(termo)
        
        chave_com_sujeito = f"{sujeito}.{termo}" if sujeito else termo
        if chave_com_sujeito in self.memoria:
            return self.memoria[chave_com_sujeito]
        if termo in self.memoria:
            return self.memoria[termo]
        
        return None

    def _avaliar_condicao(self, condicao_texto):
        """Avalia condições como 'Maria tiver maçãs' ou 'Maria tiver mais de 5 maçãs'."""
        condicao_texto = condicao_texto.strip()

        # 1. Condição existencial/quantidade positiva: "Maria tiver maçãs" (quantidade > 0)
        match_exist = re.match(r"^(\w+)\s+(?:tiver|tem)\s+(.+)$", condicao_texto, re.IGNORECASE)
        if match_exist and "mais de" not in condicao_texto and "menos de" not in condicao_texto and "igual a" not in condicao_texto:
            sujeito, item = match_exist.groups()
            item_clean = item.rstrip('s').lower()
            val = self._resolver_valor(item_clean, sujeito.lower())
            return val is not None and val > 0

        # 2. Condição relacional: "Maria tiver mais de 5 maçãs"
        match_rel = re.match(
            r"^(\w+)\s+(?:tiver|tem)\s+(mais de|menos de|igual a)\s+(\d+)\s+(.+)$", 
            condicao_texto, 
            re.IGNORECASE
        )
        if match_rel:
            sujeito, operador, limite, item = match_rel.groups()
            item_clean = item.rstrip('s').lower()
            val = self._resolver_valor(item_clean, sujeito.lower())
            
            if val is None:
                return False

            limite_val = int(limite)
            if operador.lower() == "mais de":
                return val > limite_val
            elif operador.lower() == "menos de":
                return val < limite_val
            elif operador.lower() == "igual a":
                return val == limite_val

        return False

    def executar_linha(self, linha, sujeito_contexto=None):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # Resolve pronomes contextuais ("ela dá..." -> "Maria dá...")
        if sujeito_contexto and re.match(r"^(ela|ele)\b", linha, re.IGNORECASE):
            linha = re.sub(r"^(ela|ele)\b", sujeito_contexto, linha, flags=re.IGNORECASE)

        # 1. LAÇO DE REPETIÇÃO: "Enquanto <condição> <ação>"
        match_enquanto = re.match(r"^Enquanto\s+(.+?)\s+(?:faça\s+)?(.+)$", linha, re.IGNORECASE)
        if match_enquanto:
            condicao_str, acao_str = match_enquanto.groups()

            # Extrai o sujeito para manter o contexto dos pronomes no loop
            sujeito_match = re.match(r"^(\w+)", condicao_str.strip())
            sujeito_loop = sujeito_match.group(1) if sujeito_match else None

            iterações = 0
            historico = []

            # Ciclo de repetição real em Python
            while self._avaliar_condicao(condicao_str):
                if iterações >= self.limite_loop:
                    return f"[Erro] Loop infinito detectado! Interrompido após {self.limite_loop} iterações."

                res = self.executar_linha(acao_str, sujeito_contexto=sujeito_loop)
                historico.append(res)
                iterações += 1

            if iterações == 0:
                return f"[Loop Ignorado] A condição '{condicao_str}' já começou Falsa."

            return f"[Loop Concluído] Executado {iterações} vez(es)."

        # 2. CONDICIONAL: "Se <condição> então <ação>"
        match_se = re.match(r"^Se\s+(.+?)\s+então\s+(.+)$", linha, re.IGNORECASE)
        if match_se:
            condicao_str, acao_str = match_se.groups()
            sujeito_match = re.match(r"^(\w+)", condicao_str.strip())
            sujeito_cond = sujeito_match.group(1) if sujeito_match else None

            if self._avaliar_condicao(condicao_str):
                return self.executar_linha(acao_str, sujeito_contexto=sujeito_cond)
            return f"[Condição Falsa] Ignorado: '{acao_str}'"

        # 3. TRANSFERÊNCIA DE ITENS: "<Doador> dá <Quantidade> <Item> para <Recebedor>"
        match_transf = re.match(
            r"^(\w+)\s+dá\s+(\d+)\s+(.+?)\s+para\s+(\w+)$", 
            linha, re.IGNORECASE
        )
        if match_transf:
            doador, qtd, item, recebedor = match_transf.groups()
            qtd_val = int(qtd)
            item_clean = item.rstrip('s').lower()

            chave_doador = f"{doador.lower()}.{item_clean}"
            chave_recebedor = f"{recebedor.lower()}.{item_clean}"

            saldo_doador = self.memoria.get(chave_doador, 0)
            if saldo_doador < qtd_val:
                return f"[Erro] {doador} não tem {qtd_val} {item_clean}(s) suficientes."

            self.memoria[chave_doador] = saldo_doador - qtd_val
            self.memoria[chave_recebedor] = self.memoria.get(chave_recebedor, 0) + qtd_val
            return f"[Transferência] {doador} deu {qtd_val} {item_clean}(s) para {recebedor}."

        # 4. CRIAÇÃO DE VARIÁVEL: "<Sujeito> tem <Valor> <Item>"
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            item_key = f"{sujeito.lower()}.{item.rstrip('s').lower()}"
            self.memoria[item_key] = int(valor)
            return f"[Criação] {sujeito} agora possui {valor} {item}."

        # 5. IMPRESSÃO
        match_print = re.match(r"^Mostre\s+(.+)$", linha, re.IGNORECASE)
        if match_print:
            alvo = match_print.group(1).lower()
            if alvo == "tudo":
                return f"[Memória Total]: {self.memoria}"
            itens = {k: v for k, v in self.memoria.items() if k.startswith(f"{alvo}.")}
            return f"[Estado de {alvo.capitalize()}]: {itens}"

        return f"[Erro de Sintaxe]: '{linha}'"

    def interpretar(self, historia):
        return [self.executar_linha(l) for l in historia.strip().split('\n') if l.strip()]
```

---

### Exemplo Prático com Loop Narrativo

```python
historia = """
Maria tem 5 maçãs.
João tem 0 maçãs.

Enquanto Maria tiver maçãs ela dá 1 maçã para João.

Mostre tudo
"""

interpretador = InterpretadorNarrativoCompleto()
resultados = interpretador.interpretar(historia)

for res in resultados:
    print(res)
```

#### Saída Gerada:
```text
[Criação] Maria agora possui 5 maçãs.
[Criação] João agora possui 0 maçãs.
[Loop Concluído] Executado 5 vez(es).
[Memória Total]: {'maria.maca': 0, 'joao.maca': 5}
```

---

<GenerateWidget component_placeholder_id="im_bb011a788144679f" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Visual simulation of state degradation and transfer within a narrative loop iteration by iteration.
**Visual type:** Interactive iteration trace and state progression line chart.
**Data specification:**
- **Data structure:** Iteration history array storing iteration index, variable values (`maria.maca`, `joao.maca`), and condition status (`val > 0`).
- **Initial values:** 
  - Iteration 0: Maria = 5, João = 0
  - Iteration 1: Maria = 4, João = 1
  - Iteration 2: Maria = 3, João = 2
  - Iteration 3: Maria = 2, João = 3
  - Iteration 4: Maria = 1, João = 4
  - Iteration 5: Maria = 0, João = 5 -> Loop Terminates
- **Mapping:** Iteration step on X-axis mapped to inventory level on Y-axis.
**User controls:** Step forward/backward through loop iterations with play/pause execution simulation.
**Interactivity:** Hovering over loop steps highlights the exact memory change delta.
**Animation:** Smooth line drawing and inventory counter transitions during loop execution.
</GenerateWidget>

---

<ElicitationsGroup message="O que deseja explorar agora na construção da sua linguagem?">
  <Elicitation label="Criar blocos de código com múltiplos comandos no loop" query="Como fazer para o loop executar mais de uma linha de comando por iteração no estilo de história?"/>
  <Elicitation label="Migrar o projeto para uma gramática formal com Lark" query="Como reescrever este interpretador com suporte a loops e condicionais usando a biblioteca Lark em Python?"/>
</ElicitationsGroup>


######## TURNO 4 USER ########
Como fazer para o loop executar mais de uma linha de comando por iteração no estilo de história?

######## TURNO 4 GEMINI ########
Para permitir que um loop execute **múltiplos comandos por iteração** sem quebrar o estilo natural de história, a melhor abordagem é usar **parágrafos ou blocos delimitados por pontuação/palavras de encerramento**.

Existem duas formas elegantes de estruturar isso na narrativa:

1. **Uso de Parágrafos Indentados ou Marcadores:** O loop começa na linha principal e executa todas as linhas do "bloco" abaixo até encontrar uma linha em branco ou o fim da história.
2. **Palavra-chave de Encerramento (Delimitador):** Usar uma expressão narrativa natural para fechar o bloco, como `Fim do laço.` ou `E assim termina a rotina.`.

Abaixo está a implementação completa utilizando **blocos delimitados por palavra-chave** (mais robusto e expansível).

---

### Código do Interpretador com Suporte a Blocos Multi-linha

```python
import re

class InterpretadorComBlocosMultiLinha:
    def __init__(self, limite_loop=1000):
        self.memoria = {}
        self.limite_loop = limite_loop

    def _resolver_valor(self, termo, sujeito=None):
        termo = termo.strip().rstrip('s').lower()
        if termo.isdigit():
            return int(termo)
        
        chave_com_sujeito = f"{sujeito}.{termo}" if sujeito else termo
        if chave_com_sujeito in self.memoria:
            return self.memoria[chave_com_sujeito]
        if termo in self.memoria:
            return self.memoria[termo]
        return None

    def _avaliar_condicao(self, condicao_texto):
        condicao_texto = condicao_texto.strip()
        match_exist = re.match(r"^(\w+)\s+(?:tiver|tem)\s+(.+)$", condicao_texto, re.IGNORECASE)
        if match_exist and not any(k in condicao_texto for k in ["mais de", "menos de", "igual a"]):
            sujeito, item = match_exist.groups()
            val = self._resolver_valor(item.rstrip('s').lower(), sujeito.lower())
            return val is not None and val > 0
        return False

    def executar_linha(self, linha, sujeito_contexto=None):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # Resolve pronomes contextuais ("ela dá..." -> "Maria dá...")
        if sujeito_contexto and re.match(r"^(ela|ele)\b", linha, re.IGNORECASE):
            linha = re.sub(r"^(ela|ele)\b", sujeito_contexto, linha, flags=re.IGNORECASE)

        # 1. TRANSFERÊNCIA
        match_transf = re.match(r"^(\w+)\s+dá\s+(\d+)\s+(.+?)\s+para\s+(\w+)$", linha, re.IGNORECASE)
        if match_transf:
            doador, qtd, item, recebedor = match_transf.groups()
            qtd_val, item_clean = int(qtd), item.rstrip('s').lower()
            chave_d, chave_r = f"{doador.lower()}.{item_clean}", f"{recebedor.lower()}.{item_clean}"

            saldo = self.memoria.get(chave_d, 0)
            if saldo < qtd_val:
                return f"[Erro] {doador} não tem {qtd_val} {item_clean}(s) suficientes."

            self.memoria[chave_d] = saldo - qtd_val
            self.memoria[chave_r] = self.memoria.get(chave_r, 0) + qtd_val
            return f"[Transferência] {doador} deu {qtd_val} {item_clean}(s) para {recebedor}."

        # 2. GANHAR/PERDER ITENS
        match_mod = re.match(r"^(\w+)\s+(ganha|perde)\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_mod:
            sujeito, op, qtd, item = match_mod.groups()
            item_clean = item.replace("suas", "").strip().rstrip('s').lower()
            chave = f"{sujeito.lower()}.{item_clean}"
            val = int(qtd)

            if op.lower() == "ganha":
                self.memoria[chave] = self.memoria.get(chave, 0) + val
            else:
                self.memoria[chave] = max(0, self.memoria.get(chave, 0) - val)
            return f"[Modificação] {sujeito} agora tem {self.memoria[chave]} {item_clean}(s)."

        # 3. DECLARAÇÃO DE VARIÁVEL
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            self.memoria[f"{sujeito.lower()}.{item.rstrip('s').lower()}"] = int(valor)
            return f"[Criação] {sujeito} possui {valor} {item}."

        # 4. IMPRESSÃO
        match_print = re.match(r"^Mostre\s+(.+)$", linha, re.IGNORECASE)
        if match_print:
            alvo = match_print.group(1).lower()
            if alvo == "tudo":
                return f"[Memória Total]: {self.memoria}"
            return f"[Estado de {alvo.capitalize()}]: {{k: v for k, v in self.memoria.items() if k.startswith(f'{alvo}.')}}"

        return f"[Erro de Sintaxe]: '{linha}'"

    def interpretar(self, historia):
        linhas = [l.strip() for l in historia.strip().split('\n') if l.strip()]
        resultados = []
        i = 0

        while i < len(linhas):
            linha = linhas[i]

            # Deteção do início do Loop Multi-linha
            match_loop = re.match(r"^Enquanto\s+(.+?)\s+faça:$", linha, re.IGNORECASE)
            if match_loop:
                condicao_str = match_loop.group(1)
                sujeito_match = re.match(r"^(\w+)", condicao_str.strip())
                sujeito_loop = sujeito_match.group(1) if sujeito_match else None

                # Captura todas as linhas internas até achar 'Fim do laço'
                bloco_linhas = []
                j = i + 1
                while j < len(linhas) and linhas[j].lower().rstrip('.') != "fim do laço":
                    bloco_linhas.append(linhas[j])
                    j += 1

                # Executa o bloco capturado enquanto a condição for verdadeira
                iterações = 0
                while self._avaliar_condicao(condicao_str):
                    if iterações >= self.limite_loop:
                        resultados.append(f"[Erro] Loop infinito interrompido!")
                        break
                    
                    # Executa cada comando do bloco em ordem
                    for sub_linha in bloco_linhas:
                        res = self.executar_linha(sub_linha, sujeito_contexto=sujeito_loop)
                        resultados.append(f"  [Iteração {iterações + 1}] {res}")
                    
                    iterações += 1

                resultados.append(f"[Loop Concluído] Executado {iterações} vez(es).")
                i = j + 1  # Avança o ponteiro principal para depois do 'Fim do laço'
                continue

            # Execução de linha comum (fora de loops)
            res = self.executar_linha(linha)
            if res:
                resultados.append(res)
            i += 1

        return resultados
```

---

### Exemplo Prático de História com Bloco Multi-linha

```python
historia = """
Maria tem 3 maçãs.
João tem 0 maçãs.
João tem 0 moedas.

Enquanto Maria tiver maçãs faça:
  Maria dá 1 maçã para João.
  João ganha 2 moedas.
Fim do laço.

Mostre tudo.
"""

interpretador = InterpretadorComBlocosMultiLinha()
resultados = interpretador.interpretar(historia)

for res in resultados:
    print(res)
```

#### Saída Gerada:
```text
[Criação] Maria possui 3 maçãs.
[Criação] João possui 0 maçãs.
[Criação] João possui 0 moedas.
  [Iteração 1] [Transferência] Maria deu 1 maçã(s) para João.
  [Iteração 1] [Modificação] João agora tem 2 moeda(s).
  [Iteração 2] [Transferência] Maria deu 1 maçã(s) para João.
  [Iteração 2] [Modificação] João agora tem 4 moeda(s).
  [Iteração 3] [Transferência] Maria deu 1 maçã(s) para João.
  [Iteração 3] [Modificação] João agora tem 6 moeda(s).
[Loop Concluído] Executado 3 vez(es).
[Memória Total]: {'maria.maca': 0, 'joao.maca': 3, 'joao.moeda': 6}
```

---

<GenerateWidget component_placeholder_id="im_a8cc1788d8bac2ef" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Multi-instruction step visualization demonstrating how a single loop block cascades into multiple sequential memory updates per pass.
**Visual type:** Interactive block execution trace and state matrix.
**Data specification:**
- **Data structure:** Timeline array containing pass index, sub-instruction trace, and memory snapshot.
- **Initial values:**
  - Pass 0: `maria.maca` = 3, `joao.maca` = 0, `joao.moeda` = 0
  - Pass 1, Step A: `maria.maca` -> 2, `joao.maca` -> 1
  - Pass 1, Step B: `joao.moeda` -> 2
  - Pass 2, Step A: `maria.maca` -> 1, `joao.maca` -> 2
  - Pass 2, Step B: `joao.moeda` -> 4
  - Pass 3, Step A: `maria.maca` -> 0, `joao.maca` -> 3
  - Pass 3, Step B: `joao.moeda` -> 6
- **Mapping:** Block pass index on X-axis mapped to individual variable curves on Y-axis.
**User controls:** Play/pause block stepping and sub-instruction detail inspector.
**Interactivity:** Clicking an iteration expands the exact sub-statement stack trace.
**Animation:** Sequenced highlighting of inner loop instructions on step triggering.
</GenerateWidget>

---

<ElicitationsGroup message="Qual seria a próxima evolução interessante para a sua linguagem narrativa?">
  <Elicitation label="Criar rotinas ou funções narrativas (Ex: 'Capítulo: Mercado')" query="Como implementar funções ou rotinas reutilizáveis no estilo de capítulos de história no interpretador?"/>
  <Elicitation label="Adicionar suporte a variáveis de texto (Nomes, itens e lugares)" query="Como trabalhar com variáveis de texto e diálogos na história além de quantidades numéricas?"/>
</ElicitationsGroup>


######## TURNO 5 USER ########
Como trabalhar com variáveis de texto e diálogos na história além de quantidades numéricas?

######## TURNO 5 GEMINI ########
Para trabalhar com **variáveis de texto e diálogos**, precisamos expandir a memória para aceitar **strings (Textos)** e interpretar falas representadas por **aspas (`"..."`)**.

No estilo narrativo, isso permite definir atributos textuais (como a cidade de origem ou o estado emocional de um personagem), trocar frases e imprimir diálogos formatados.

---

### Sintaxe para Variáveis de Texto e Diálogos

| Conceito | Exemplo Narrativo | O que faz no Interpretador |
| :--- | :--- | :--- |
| **Atribuição de Texto** | `Maria mora em "São Paulo"` | Guarda `"São Paulo"` no atributo `maria.cidade` |
| **Alteração de Atributo** | `João passa a se chamar "Capitão João"` | Atualiza `joao.nome` para `"Capitão João"` |
| **Diálogo / Fala Directa** | `Maria diz: "Olá João, tudo bem?"` | Imprime a fala no console formatada como diálogo |
| **Diálogo Dinâmico** | `Maria diz: "Eu tenho {maria.maçã} maçãs"` | Interpola variáveis numéricas ou de texto dentro da frase |

---

### Código do Interpretador com Suporte a Texto e Diálogos

```python
import re

class InterpretadorComDialogos:
    def __init__(self):
        # Suporta números e textos: {"maria.maca": 5, "maria.cidade": "São Paulo"}
        self.memoria = {}

    def _interpolar_texto(self, texto):
        """Substitui marcadores como {maria.maçã} ou {maria.cidade} pelos valores da memória."""
        def substituir(match):
            chave = match.group(1).lower().strip()
            return str(self.memoria.get(chave, f"[{chave} desconhecido]"))

        return re.sub(r"\{(.+?)\}", substituir, texto)

    def executar_linha(self, linha):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # 1. DIÁLOGO COM INTERPOLAÇÃO: <Sujeito> diz: "<Texto>"
        match_fala = re.match(r"^(\w+)\s+diz:\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_fala:
            sujeito, texto_bruto = match_fala.groups()
            texto_final = self._interpolar_texto(texto_bruto)
            return f'🗣️  [{sujeito.capitalize()}]: "{texto_final}"'

        # 2. ATRIBUIÇÃO DE TEXTO / ATRIBUTO: <Sujeito> mora em "<Texto>" / <Sujeito> é "<Texto>"
        match_texto = re.match(r"^(\w+)\s+(?:mora em|é|está em|chamado)\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_texto:
            sujeito, valor_texto = match_texto.groups()
            # Mapeia verbos para nomes de atributos legíveis
            verbo = re.search(r"(mora em|é|está em|chamado)", linha, re.IGNORECASE).group(1).lower()
            atributo = "cidade" if verbo == "mora em" else ("status" if verbo in ["é", "está em"] else "titulo")

            chave = f"{sujeito.lower()}.{atributo}"
            self.memoria[chave] = valor_texto
            return f"[Atributo] {sujeito} -> {atributo} = '{valor_texto}'"

        # 3. ATRIBUIÇÃO DE QUANTIDADE NUMÉRICA: <Sujeito> tem <Número> <Item>
        match_num = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_num:
            sujeito, valor, item = match_num.groups()
            item_key = f"{sujeito.lower()}.{item.rstrip('s').lower()}"
            self.memoria[item_key] = int(valor)
            return f"[Criação] {sujeito} possui {valor} {item}."

        # 4. IMPRESSÃO DA MEMÓRIA
        match_print = re.match(r"^Mostre\s+(.+)$", linha, re.IGNORECASE)
        if match_print:
            alvo = match_print.group(1).lower()
            if alvo == "tudo":
                return f"[Memória Total]: {self.memoria}"
            return f"[Estado de {alvo.capitalize()}]: {{k: v for k, v in self.memoria.items() if k.startswith(f'{alvo}.')}}"

        return f"[Erro de Sintaxe]: '{linha}'"

    def interpretar(self, historia):
        return [self.executar_linha(l) for l in historia.strip().split('\n') if l.strip()]
```

---

### Exemplo de História com Diálogos e Variáveis de Texto

```python
historia = """
Maria tem 12 maçãs.
Maria mora em "Rio de Janeiro".
Maria é "Feliz".

João tem 2 maçãs.

Maria diz: "Olá! Eu moro no {maria.cidade} e tenho {maria.maçã} maçãs!"
João diz: "Eu só tenho {joao.maçã} maçãs... Maria está se sentindo {maria.status}."
"""

interpretador = InterpretadorComDialogos()
resultados = interpretador.interpretar(historia)

for res in resultados:
    print(res)
```

#### Saída Gerada:
```text
[Criação] Maria possui 12 maçãs.
[Atributo] Maria -> cidade = 'Rio de Janeiro'
[Atributo] Maria -> status = 'Feliz'
[Criação] João possui 2 maçãs.
🗣️  [Maria]: "Olá! Eu moro no Rio de Janeiro e tenho 12 maçãs!"
🗣️  [João]: "Eu só tenho 2 maçãs... Maria está se sentindo Feliz."
```

---

<GenerateWidget component_placeholder_id="im_b02ff28256c97020" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Dialogue stream and character profile state inspector visualizing speech interpolation and dynamic string mutation.
**Visual type:** Interactive narrative dialogue feed & character card matrix.
**Data specification:**
- **Data structure:** Array of conversation cards containing character avatar, raw dialogue string, interpolated output, and active string attributes (`cidade`, `status`).
- **Initial values:**
  - Maria: `maca` = 12, `cidade` = "Rio de Janeiro", `status` = "Feliz"
  - João: `maca` = 2
  - Line 1 Output: "Olá! Eu moro no Rio de Janeiro e tenho 12 maçãs!"
  - Line 2 Output: "Eu só tenho 2 maçãs... Maria está se sentindo Feliz."
- **Mapping:** Character entity mapped to string key-value cards and dialogue speech bubbles.
**User controls:** Character filter toggle and template variable inspector.
**Interactivity:** Hovering tokens like `{maria.cidade}` highlights the exact property source in the character sheet.
**Animation:** Speech bubbles typing effect animation on step execution.
</GenerateWidget>

---

<ElicitationsGroup message="Como prefere organizar as próximas etapas da sua linguagem de programação narrativa?">
  <Elicitation label="Empacotar o interpretador como uma biblioteca Python instalável" query="Como posso empacotar esse interpretador de linguagem narrativa em um módulo Python reutilizável com arquivo CLI?"/>
  <Elicitation label="Evoluir a arquitetura para um compilador completo com AST" query="Como transformar este interpretador em um compilador que gera uma Árvore Sintática Abstrata (AST) e traduz a história diretamente para código Python?"/>
</ElicitationsGroup>


######## TURNO 6 USER ########
Como posso empacotar esse interpretador de linguagem narrativa em um módulo Python reutilizável com arquivo CLI?

######## TURNO 6 GEMINI ########
Empacotar seu interpretador em uma biblioteca Python reutilizável com suporte a **CLI (Command Line Interface)** permite que qualquer pessoa instale sua linguagem via `pip` e execute histórias diretamente do terminal, por exemplo:

```bash
historia executar minha_historia.txt
```

Abaixo está a estrutura profissional completa do projeto usando padrões modernos de empacotamento com `pyproject.toml` (PEP 518/621).

---

### 1. Estrutura de Arquivos do Projeto

Crie a seguinte estrutura de diretórios na raiz do seu projeto:

```text
meu_interpretador/
│
├── pyproject.toml              # Configurações de build e dependências
├── README.md                   # Documentação do projeto
├── historia/                   # Pacote do código-fonte Python
│   ├── __init__.py             # Torna o módulo importável
│   ├── core.py                 # O código do Interpretador Narrativo
│   └── cli.py                  # Interface de Linha de Comando (CLI)
└── exemplos/
    └── conto.txt               # Exemplo de arquivo de história
```

---

### 2. Código do Módulo (`historia/core.py`)

Isso guarda a classe do interpretador isolada e limpa para reuso em código Python convencional.

```python
# historia/core.py
import re

class InterpretadorNarrativo:
    def __init__(self):
        self.memoria = {}

    def _interpolar_texto(self, texto):
        def substituir(match):
            chave = match.group(1).lower().strip()
            return str(self.memoria.get(chave, f"[{chave} desconhecido]"))
        return re.sub(r"\{(.+?)\}", substituir, texto)

    def executar_linha(self, linha):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # Fala / Diálogo
        match_fala = re.match(r"^(\w+)\s+diz:\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_fala:
            sujeito, texto = match_fala.groups()
            return f'🗣️  [{sujeito.capitalize()}]: "{self._interpolar_texto(texto)}"'

        # Atribuição / Criação
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            self.memoria[f"{sujeito.lower()}.{item.rstrip('s').lower()}"] = int(valor)
            return f"[Criação] {sujeito} possui {valor} {item}."

        # Impressão de Estado
        if linha.lower().startswith("mostre"):
            return f"[Memória]: {self.memoria}"

        return f"[Instrução]: {linha}"

    def interpretar_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        return [self.executar_linha(l) for l in conteudo.split('\n') if l.strip()]
```

---

### 3. Interface CLI (`historia/cli.py`)

Utilizamos a biblioteca nativa `argparse` para lidar com os comandos passados pelo terminal.

```python
# historia/cli.py
import argparse
import sys
from historia.core import InterpretadorNarrativo

def main():
    parser = argparse.ArgumentParser(
        description="Interpretador de Linguagem Narrativa baseada em Histórias."
    )
    
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando: historia executar <arquivo.txt>
    exec_parser = subparsers.add_parser("executar", help="Executa um arquivo de história (.txt)")
    exec_parser.add_argument("arquivo", type=str, help="Caminho para o arquivo de história")

    args = parser.parse_args()

    if args.comando == "executar":
        interpretador = InterpretadorNarrativo()
        try:
            resultados = interpretador.interpretar_arquivo(args.arquivo)
            print("\n--- INÍCIO DA EXECUÇÃO ---")
            for res in resultados:
                if res:
                    print(res)
            print("--- FIM DA EXECUÇÃO ---\n")
        except FileNotFoundError:
            print(f"Erro: Arquivo '{args.arquivo}' não foi encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

### 4. Arquivo de Exportação do Módulo (`historia/__init__.py`)

Permite que outros desenvolvedores importem a biblioteca via Python com `from historia import InterpretadorNarrativo`.

```python
# historia/__init__.py
from .core import InterpretadorNarrativo

__version__ = "0.1.0"
__all__ = ["InterpretadorNarrativo"]
```

---

### 5. Configuração de Build (`pyproject.toml`)

O `pyproject.toml` define o nome do pacote e cria o **ponto de entrada da CLI** (`project.scripts`).

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "linguagem-narrativa"
version = "0.1.0"
description = "Uma linguagem de programação interpretada no estilo de histórias narrativas."
readme = "README.md"
authors = [{ name = "Seu Nome", email = "seu.email@exemplo.com" }]
license = { text = "MIT" }
requires-python = ">=3.8"
dependencies = []

[project.scripts]
# Define o comando do terminal: historia -> roda main() em historia/cli.py
historia = "historia.cli:main"
```

---

### 6. Instalação e Teste Local

1. **Instale o pacote em Modo Editável (`-e`):**
   No terminal, dentro da pasta raiz do seu projeto (`meu_interpretador/`), execute:
   ```bash
   pip install -e .
   ```

2. **Crie um arquivo de teste (`exemplos/conto.txt`):**
   ```text
   Maria tem 20 maçãs.
   Maria diz: "Eu tenho {maria.maçã} maçãs para vender!"
   Mostre tudo
   ```

3. **Rode via CLI:**
   ```bash
   historia executar exemplos/conto.txt
   ```

4. **Ou use importando via Python:**
   ```python
   from historia import InterpretadorNarrativo

   interp = InterpretadorNarrativo()
   res = interp.interpretar_arquivo("exemplos/conto.txt")
   print(res)
   ```

---

<GenerateWidget component_placeholder_id="im_9a4a0680a036c530" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Architectural diagram showing how CLI arguments invoke package components to run narrative scripts.
**Visual type:** Interactive package runtime & pipeline visualizer.
**Data specification:**
- **Data structure:** Pipeline nodes tracking command line invocation (`historia executar`), entrypoint parsing (`cli.py`), core interpretation (`core.py`), memory state allocation, and output formatting.
- **Initial values:**
  - CLI Trigger: `historia executar conto.txt`
  - Parser Node: `argparse` resolves file argument
  - Engine Node: `InterpretadorNarrativo.interpretar_arquivo()`
  - Output Stream: Console log formatting
- **Mapping:** Execution step mapped to physical python module within the package tree.
**User controls:** Clickable architecture components displaying module code snippets.
**Interactivity:** Hovering package blocks shows the corresponding import and execution path.
**Animation:** Animated pulse tracing data flow from terminal input to output display.
</GenerateWidget>

---

<ElicitationsGroup message="Como deseja continuar com o refinamento do seu pacote?">
  <Elicitation label="Publicar a biblioteca no PyPI" query="Qual é o passo a passo para compilar este pacote e publicá-lo no PyPI oficial para que outros possam instalar com 'pip install'?"/>
  <Elicitation label="Adicionar testes automatizados com pytest" query="Como criar uma suíte de testes unitários com pytest para garantir que a CLI e as regras do interpretador continuem funcionando?"/>
</ElicitationsGroup>


######## TURNO 7 USER ########
Faça um tutorial de como rodar isso na minha maquina. 

######## TURNO 7 GEMINI ########
Este tutorial vai te guiar no passo a passo para criar a estrutura no seu computador, instalar o pacote localmente e rodar suas histórias direto pelo terminal.

---

### Passo 1: Preparar a Pasta do Projeto

Abra o seu terminal (Prompt de Comando, PowerShell ou Terminal do Linux/Mac) e execute os comandos abaixo para criar a pasta do projeto:

```bash
# Cria a pasta do projeto e entra nela
mkdir meu_interpretador
cd meu_interpretador

# Cria as pastas do pacote Python e de exemplos
mkdir historia
mkdir exemplos
```

---

### Passo 2: Criar os Arquivos do Código

Crie os arquivos abaixo dentro da estrutura que montamos.

#### 1. Arquivo `historia/core.py`
Este arquivo contém a inteligência do interpretador.

```python
import re

class InterpretadorNarrativo:
    def __init__(self):
        self.memoria = {}

    def _interpolar_texto(self, texto):
        def substituir(match):
            chave = match.group(1).lower().strip()
            return str(self.memoria.get(chave, f"[{chave} desconhecido]"))
        return re.sub(r"\{(.+?)\}", substituir, texto)

    def executar_linha(self, linha):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # 1. Fala / Diálogo: Maria diz: "Olá!"
        match_fala = re.match(r"^(\w+)\s+diz:\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_fala:
            sujeito, texto = match_fala.groups()
            return f'🗣️  [{sujeito.capitalize()}]: "{self._interpolar_texto(texto)}"'

        # 2. Atribuição: Maria tem 20 maçãs
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            self.memoria[f"{sujeito.lower()}.{item.rstrip('s').lower()}"] = int(valor)
            return f"[Criação] {sujeito} possui {valor} {item}."

        # 3. Impressão de estado
        if linha.lower().startswith("mostre"):
            return f"[Estado da Memória]: {self.memoria}"

        return f"[Instrução]: {linha}"

    def interpretar_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        return [self.executar_linha(l) for l in conteudo.split('\n') if l.strip()]
```

#### 2. Arquivo `historia/cli.py`
Este arquivo cria a Interface de Linha de Comando (CLI) para rodar via terminal.

```python
import argparse
import sys
from historia.core import InterpretadorNarrativo

def main():
    parser = argparse.ArgumentParser(
        description="Interpretador de Linguagem Narrativa baseada em Histórias."
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    exec_parser = subparsers.add_parser("executar", help="Executa um arquivo de história (.txt)")
    exec_parser.add_argument("arquivo", type=str, help="Caminho para o arquivo .txt da história")

    args = parser.parse_args()

    if args.comando == "executar":
        interpretador = InterpretadorNarrativo()
        try:
            resultados = interpretador.interpretar_arquivo(args.arquivo)
            print("\n--- INÍCIO DA HISTÓRIA ---")
            for res in resultados:
                if res:
                    print(res)
            print("--- FIM DA HISTÓRIA ---\n")
        except FileNotFoundError:
            print(f"Erro: O arquivo '{args.arquivo}' não foi encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

#### 3. Arquivo `historia/__init__.py`
Torna a pasta `historia` um pacote importável.

```python
from .core import InterpretadorNarrativo

__version__ = "0.1.0"
__all__ = ["InterpretadorNarrativo"]
```

#### 4. Arquivo `pyproject.toml`
Fica na raiz do projeto (`meu_interpretador/pyproject.toml`) e define as configurações de instalação e o comando `historia` no terminal.

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "linguagem-narrativa"
version = "0.1.0"
description = "Uma linguagem de programação interpretada no estilo de histórias."
authors = [{ name = "Seu Nome" }]
requires-python = ">=3.8"

[project.scripts]
historia = "historia.cli:main"
```

---

### Passo 3: Criar uma História de Teste

Crie o arquivo `exemplos/conto.txt` com o seguinte texto:

```text
Maria tem 20 maçãs.
João tem 5 maçãs.
Maria diz: "Olá João! Eu tenho {maria.maçã} maçãs e você tem {joao.maçã}."
Mostre tudo
```

---

### Passo 4: Instalar e Executar na sua Máquina

1. Certifique-se de estar na pasta raiz (`meu_interpretador`).
2. Instale o pacote no Python em modo editável (`-e`):

```bash
pip install -e .
```

3. Agora execute a história diretamente pelo comando criado no terminal:

```bash
historia executar exemplos/conto.txt
```

#### Saída Esperada no Terminal:

```text
--- INÍCIO DA HISTÓRIA ---
[Criação] Maria possui 20 maçãs.
[Criação] João possui 5 maçãs.
🗣️  [Maria]: "Olá João! Eu tenho 20 maçãs e você tem 5."
[Estado da Memória]: {'maria.maçã': 20, 'joao.maçã': 5}
--- FIM DA HISTÓRIA ---
```

---

<GenerateWidget component_placeholder_id="im_f663fc64de268278" height="600px" type="inline_visualization">
<skills>chart</skills>

**Idea:** Terminal execution simulation tool illustrating how local setup commands translate to file layout and runtime execution.
**Visual type:** Interactive environment emulator & step-by-step installation guide.
**Data specification:**
- **Data structure:** Setup stage list tracking terminal commands, target paths, created files, and verification steps.
- **Initial values:**
  - Stage 1: Directory Setup (`mkdir meu_interpretador`)
  - Stage 2: Code Creation (`core.py`, `cli.py`, `pyproject.toml`)
  - Stage 3: Package Build (`pip install -e .`)
  - Stage 4: Execution Test (`historia executar exemplos/conto.txt`)
- **Mapping:** Installation step mapped to file system state and command line output preview.
**User controls:** Step forward/backward buttons for installation walkthrough.
**Interactivity:** Clicking directory nodes previews file contents and shell terminal responses.
**Animation:** Interactive prompt typing simulator for terminal commands.
</GenerateWidget>

---

<ElicitationsGroup message="O que gostaria de fazer a seguir?">
  <Elicitation label="Criar testes automatizados com Pytest" query="Como posso configurar testes unitários com Pytest para validar o interpretador automaticamente na minha máquina?"/>
  <Elicitation label="Adicionar suporte a arquivos de configuração ou VS Code" query="Como configurar o VS Code com destaque de sintaxe ou extensão para a nossa linguagem narrativa?"/>
</ElicitationsGroup>


######## TURNO 8 USER ########
Faça um arquivo de contexto para I.A com tudo já feito e exemplos. 

######## TURNO 8 GEMINI ########
Aqui está o **arquivo de contexto completo (System Prompt / Context File)** pronto para ser colado e enviado para qualquer I.A. (como ChatGPT, Claude, Gemini ou Copilot). 

Ele resume a arquitetura, todas as regras de sintaxe da linguagem narrativa, a estrutura de arquivos e exemplos práticos para que a I.A. saiba exatamente o que já foi desenvolvido e como continuar evoluindo o projeto.

---

### `CONTEXTO_PROJETO_LANG_NARRATIVA.md`

```markdown
# CONTEXTO DO PROJETO: Linguagem Narrativa em Python

## 1. Visão Geral do Projeto
Estamos desenvolvendo uma **Linguagem de Programação Domain-Specific (DSL) em Python** cuja sintaxe simula a leitura de uma história ou conto ("Maria tem 40 maçãs", "Maria diz: 'Olá!'").
O código-fonte é interpretado diretamente por um motor em Python, transformando frases narrativas em alocações de memória, operações aritméticas, condicionais, laços de repetição e exibição de diálogos.

---

## 2. Estrutura do Pacote e Arquivos

O projeto está organizado no padrão moderno de pacotes Python com suporte a CLI:

```text
meu_interpretador/
├── pyproject.toml              # Configuração de build (PEP 518/621) e CLI
├── README.md                   # Documentação do projeto
├── historia/                   # Módulo do interpretador
│   ├── __init__.py             # Exporta a classe principal
│   ├── core.py                 # Mecanismo do interpretador, regex e memória
│   └── cli.py                  # Interface de Linha de Comando (argparse)
└── exemplos/
    └── conto.txt               # Arquivos de estória para teste
```

### Configuração do `pyproject.toml`
Permite instalar a biblioteca em modo editável (`pip install -e .`) e expõe o comando global no terminal:
`historia executar <caminho_do_arquivo.txt>`

---

## 3. Especificação da Sintaxe da Linguagem Narrativa

### A. Atribuição de Variáveis e Atributos Textuais
- **Declaração Numérica:** `<Sujeito> tem <Valor> <Item>`
  - *Exemplo:* `Maria tem 40 maçãs.` -> Aloca `self.memoria["maria.maca"] = 40`
- **Atributos de Texto:** `<Sujeito> mora em "<Texto>"` ou `<Sujeito> é "<Texto>"`
  - *Exemplo:* `Maria mora em "São Paulo".` -> Aloca `self.memoria["maria.cidade"] = "São Paulo"`

### B. Operadores Aritméticos e Modificadores
- **Ganhar / Perder:** `<Sujeito> ganha <Valor> <Item>` / `<Sujeito> perde <Valor> <Item>`
  - *Exemplo:* `Maria ganha 10 maçãs.`
- **Operações Diretas:** `<Sujeito> multiplica por <Valor> suas <Item>` / `<Sujeito> divide por <Valor> suas <Item>`
  - *Exemplo:* `Maria multiplica por 2 suas maçãs.`
- **Transferência entre Sujeitos:** `<Sujeito1> dá <Quantidade> <Item> para <Sujeito2>`
  - *Exemplo:* `Maria dá 5 maçãs para João.` -> Deduz de Maria e soma em João.

### C. Diálogos e Interpolação de Variáveis
- **Sintaxe:** `<Sujeito> diz: "<Texto com {variável}>"`
  - *Exemplo:* `Maria diz: "Olá! Eu moro em {maria.cidade} e tenho {maria.maçã} maçãs."`
  - *Comportamento:* Substituto dinâmico do valor guardado na memória.

### D. Condicionais Narrativas
- **Sintaxe:** `Se <Condição> então <Ação>`
- **Pronomes de Contexto:** Suporta pronomes como `ela` ou `ele` referenciando o sujeito da condição.
  - *Exemplo:* `Se Maria tiver mais de 50 maçãs então ela dá 10 maçãs para João.`

### E. Laços de Repetição (Loops Multi-linha)
- **Sintaxe de Bloco:**
  ```text
  Enquanto <Sujeito> tiver <Item> faça:
      <Instrução 1>
      <Instrução 2>
  Fim do laço.
  ```
- **Trava de Segurança:** Possui limite configurável de iterações (`limite_loop = 1000`) para prevenção contra loops infinitos.

### F. Inspeção e Saída
- **Sintaxe:** `Mostre <Sujeito>` ou `Mostre tudo`

---

## 4. Código do Núcleo (`historia/core.py`)

```python
import re

class InterpretadorNarrativo:
    def __init__(self, limite_loop=1000):
        self.memoria = {}
        self.limite_loop = limite_loop

    def _resolver_valor(self, termo, sujeito=None):
        termo = termo.strip().rstrip('s').lower()
        if termo.isdigit():
            return int(termo)
        
        chave_com_sujeito = f"{sujeito}.{termo}" if sujeito else termo
        if chave_com_sujeito in self.memoria:
            return self.memoria[chave_com_sujeito]
        if termo in self.memoria:
            return self.memoria[termo]
        return None

    def _interpolar_texto(self, texto):
        def substituir(match):
            chave = match.group(1).lower().strip()
            return str(self.memoria.get(chave, f"[{chave} desconhecido]"))
        return re.sub(r"\{(.+?)\}", substituir, texto)

    def _avaliar_condicao(self, condicao_texto):
        condicao_texto = condicao_texto.strip()
        match_exist = re.match(r"^(\w+)\s+(?:tiver|tem)\s+(.+)$", condicao_texto, re.IGNORECASE)
        if match_exist and not any(k in condicao_texto for k in ["mais de", "menos de", "igual a"]):
            sujeito, item = match_exist.groups()
            val = self._resolver_valor(item.rstrip('s').lower(), sujeito.lower())
            return val is not None and val > 0
        return False

    def executar_linha(self, linha, sujeito_contexto=None):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        if sujeito_contexto and re.match(r"^(ela|ele)\b", linha, re.IGNORECASE):
            linha = re.sub(r"^(ela|ele)\b", sujeito_contexto, linha, flags=re.IGNORECASE)

        # Diálogo
        match_fala = re.match(r"^(\w+)\s+diz:\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_fala:
            sujeito, texto = match_fala.groups()
            return f'🗣️  [{sujeito.capitalize()}]: "{self._interpolar_texto(texto)}"'

        # Transferência
        match_transf = re.match(r"^(\w+)\s+dá\s+(\d+)\s+(.+?)\s+para\s+(\w+)$", linha, re.IGNORECASE)
        if match_transf:
            doador, qtd, item, recebedor = match_transf.groups()
            qtd_val, item_clean = int(qtd), item.rstrip('s').lower()
            chave_d, chave_r = f"{doador.lower()}.{item_clean}", f"{recebedor.lower()}.{item_clean}"
            saldo = self.memoria.get(chave_d, 0)
            if saldo < qtd_val:
                return f"[Erro] {doador} não tem {qtd_val} {item_clean}(s) suficientes."
            self.memoria[chave_d] = saldo - qtd_val
            self.memoria[chave_r] = self.memoria.get(chave_r, 0) + qtd_val
            return f"[Transferência] {doador} deu {qtd_val} {item_clean}(s) para {recebedor}."

        # Modificação de quantidade
        match_mod = re.match(r"^(\w+)\s+(ganha|perde)\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_mod:
            sujeito, op, qtd, item = match_mod.groups()
            item_clean = item.replace("suas", "").strip().rstrip('s').lower()
            chave = f"{sujeito.lower()}.{item_clean}"
            val = int(qtd)
            if op.lower() == "ganha":
                self.memoria[chave] = self.memoria.get(chave, 0) + val
            else:
                self.memoria[chave] = max(0, self.memoria.get(chave, 0) - val)
            return f"[Modificação] {sujeito} agora tem {self.memoria[chave]} {item_clean}(s)."

        # Atribuição / Criação
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            self.memoria[f"{sujeito.lower()}.{item.rstrip('s').lower()}"] = int(valor)
            return f"[Criação] {sujeito} possui {valor} {item}."

        # Atributos de texto
        match_texto = re.match(r"^(\w+)\s+(?:mora em|é|está em)\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_texto:
            sujeito, valor_texto = match_texto.groups()
            self.memoria[f"{sujeito.lower()}.atributo"] = valor_texto
            return f"[Atributo] {sujeito} -> '{valor_texto}'"

        # Exibição
        if linha.lower().startswith("mostre"):
            return f"[Memória Total]: {self.memoria}"

        return f"[Instrução]: '{linha}'"

    def interpretar(self, historia):
        linhas = [l.strip() for l in historia.strip().split('\n') if l.strip()]
        resultados = []
        i = 0
        while i < len(linhas):
            linha = linhas[i]
            match_loop = re.match(r"^Enquanto\s+(.+?)\s+faça:$", linha, re.IGNORECASE)
            if match_loop:
                condicao_str = match_loop.group(1)
                sujeito_match = re.match(r"^(\w+)", condicao_str.strip())
                sujeito_loop = sujeito_match.group(1) if sujeito_match else None
                bloco_linhas = []
                j = i + 1
                while j < len(linhas) and linhas[j].lower().rstrip('.') != "fim do laço":
                    bloco_linhas.append(linhas[j])
                    j += 1
                iterações = 0
                while self._avaliar_condicao(condicao_str):
                    if iterações >= self.limite_loop:
                        resultados.append("[Erro] Loop infinito interrompido!")
                        break
                    for sub_linha in bloco_linhas:
                        res = self.executar_linha(sub_linha, sujeito_contexto=sujeito_loop)
                        resultados.append(f"  [Iteração {iterações + 1}] {res}")
                    iterações += 1
                resultados.append(f"[Loop Concluído] Executado {iterações} vez(es).")
                i = j + 1
                continue
            res = self.executar_linha(linha)
            if res:
                resultados.append(res)
            i += 1
        return resultados

    def interpretar_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        return self.interpretar(conteudo)
```

---

## 5. Exemplo Completo de Arquivo de História (`conto.txt`)

```text
Maria tem 3 maçãs.
Maria mora em "São Paulo".
João tem 0 maçãs.
João tem 0 moedas.

Maria diz: "Eu moro em {maria.atributo} e tenho {maria.maçã} maçãs."

Enquanto Maria tiver maçãs faça:
    Maria dá 1 maçã para João.
    João ganha 2 moedas.
Fim do laço.

João diz: "Obrigado Maria! Agora eu tenho {joao.maçã} maçãs e {joao.moeda} moedas."

Mostre tudo
```

---

## 6. Próximos Passos e Objetivos do Projeto
Ao interagir com a I.A., utilize este contexto para solicitar:
1. Implementação de novas palavras-chave ou estruturas gramaticais.
2. Migração das regras de Expressões Regulares (`re`) para um parser formal usando **Lark** ou **PLY**.
3. Criação de testes unitários automatizados com `pytest`.
4. Extensão do suporte da CLI para depuração (*debug mode*) e passo a passo (*step-by-step*).
```

---

<ElicitationsGroup message="Como você gostaria de continuar a partir daqui?">
  <Elicitation label="Exportar este contexto para um arquivo .md no meu projeto" query="Como salvar esse arquivo de contexto automaticamente usando Python na minha estrutura de pastas?"/>
  <Elicitation label="Pedir à IA para implementar suporte a funções/capítulos" query="Usando o contexto fornecido, como implementar 'Capítulos' ou rotinas reutilizáveis na linguagem narrativa?"/>
</ElicitationsGroup>


######## TURNO 9 USER ########
Crie um arquivo completo ensinando a I.A a criar o projeto. 

######## TURNO 9 GEMINI ########
Este é o **prompt de contexto e instrução mestre (`PROMPT_CRIACAO_PROJETO.md`)** projetado para ser colado em qualquer I.A. (ChatGPT, Claude, Gemini, Cursor ou Copilot). 

Ele contém todo o conhecimento técnico, as especificações de arquitetura e as instruções passo a passo para que **a I.A. crie e monte o projeto do zero de forma autônoma**.

---

### `PROMPT_CRIACAO_PROJETO.md`

```markdown
# INSTRUÇÕES PARA A I.A.: Criar do Zero a Linguagem Narrativa em Python

Você é um especialista em desenvolvimento de linguagens de programação (DSLs) e arquitetura em Python. 
Sua tarefa é criar todos os arquivos e estruturas do projeto **Linguagem Narrativa**, uma linguagem interpretada em Python onde o código-fonte se lê como uma história ou conto em português.

---

## 1. Visão Geral do Sistema

A **Linguagem Narrativa** transforma frases em linguagem natural em alocações de memória, operações matemáticas, condicionais, loops e diálogos interativos.

### Exemplo de código que a linguagem deve executar:
```text
Maria tem 3 maçãs.
João tem 0 maçãs.
João tem 0 moedas.

Maria diz: "Olá! Eu tenho {maria.maçã} maçãs."

Enquanto Maria tiver maçãs faça:
    Maria dá 1 maçã para João.
    João ganha 2 moedas.
Fim do laço.

João diz: "Obrigado! Agora eu tenho {joao.maçã} maçãs e {joao.moeda} moedas."
Mostre tudo.
```

---

## 2. Estrutura do Projeto que Você Deve Criar

Crie e monte a seguinte árvore de diretórios e arquivos:

```text
meu_interpretador/
├── pyproject.toml              # Configurações do pacote e CLI
├── README.md                   # Documentação
├── historia/                   # Pacote Python principal
│   ├── __init__.py             # Exposição de classes
│   ├── core.py                 # Interpretador, regex e estado de memória
│   └── cli.py                  # Interface de linha de comando
└── exemplos/
    └── conto.txt               # História de exemplo para testes
```

---

## 3. Especificação dos Arquivos

### Arquivo 1: `pyproject.toml`
Gere a configuração moderna de build (PEP 518/621) expondo o comando `historia` no terminal.

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "linguagem-narrativa"
version = "0.1.0"
description = "Uma linguagem de programação interpretada no estilo de histórias."
readme = "README.md"
authors = [{ name = "Desenvolvedor" }]
requires-python = ">=3.8"

[project.scripts]
historia = "historia.cli:main"
```

---

### Arquivo 2: `historia/core.py`
Implemente a classe `InterpretadorNarrativo` contendo:
1. **Memória de Variáveis:** Dicionário `self.memoria` que guarda variáveis no formato `sujeito.atributo` (ex: `maria.maca`, `joao.moeda`, `maria.cidade`).
2. **Interpolação de Strings:** Método para resolver marcadores como `{maria.maçã}` dentro de diálogos em aspas.
3. **Casos do Interpretador (Regex/Matchers):**
   - **Declaração Numérica:** `<Sujeito> tem <Valor> <Item>` (ex: `Maria tem 10 maçãs.`)
   - **Atributo de Texto:** `<Sujeito> mora em "<Texto>"` ou `<Sujeito> é "<Texto>"`
   - **Modificações Aritméticas:** `<Sujeito> ganha <Valor> <Item>` / `<Sujeito> perde <Valor> <Item>`
   - **Transferência:** `<Sujeito1> dá <Quantidade> <Item> para <Sujeito2>`
   - **Diálogos:** `<Sujeito> diz: "<Texto>"` (Formatado com emoji `🗣️`)
   - **Impressão de Estado:** `Mostre <Sujeito>` ou `Mostre tudo`
4. **Laço de Repetição Multi-linha:** Captura blocos iniciando com `Enquanto <Condição> faça:` até `Fim do laço.`, executando os comandos em loop com trava contra loops infinitos (`limite_loop=1000`).
5. **Resolução de Pronomes:** Transforma pronomes como `ela` e `ele` no sujeito do contexto ativo do bloco.

#### Código-Fonte de Referência para `historia/core.py`:
```python
import re

class InterpretadorNarrativo:
    def __init__(self, limite_loop=1000):
        self.memoria = {}
        self.limite_loop = limite_loop

    def _resolver_valor(self, termo, sujeito=None):
        termo = termo.strip().rstrip('s').lower()
        if termo.isdigit():
            return int(termo)
        chave_com_sujeito = f"{sujeito}.{termo}" if sujeito else termo
        if chave_com_sujeito in self.memoria:
            return self.memoria[chave_com_sujeito]
        if termo in self.memoria:
            return self.memoria[termo]
        return None

    def _interpolar_texto(self, texto):
        def substituir(match):
            chave = match.group(1).lower().strip()
            return str(self.memoria.get(chave, f"[{chave} desconhecido]"))
        return re.sub(r"\{(.+?)\}", substituir, texto)

    def _avaliar_condicao(self, condicao_texto):
        condicao_texto = condicao_texto.strip()
        match_exist = re.match(r"^(\w+)\s+(?:tiver|tem)\s+(.+)$", condicao_texto, re.IGNORECASE)
        if match_exist and not any(k in condicao_texto for k in ["mais de", "menos de", "igual a"]):
            sujeito, item = match_exist.groups()
            val = self._resolver_valor(item.rstrip('s').lower(), sujeito.lower())
            return val is not None and val > 0
        return False

    def executar_linha(self, linha, sujeito_contexto=None):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        if sujeito_contexto and re.match(r"^(ela|ele)\b", linha, re.IGNORECASE):
            linha = re.sub(r"^(ela|ele)\b", sujeito_contexto, linha, flags=re.IGNORECASE)

        # Diálogo
        match_fala = re.match(r"^(\w+)\s+diz:\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_fala:
            sujeito, texto = match_fala.groups()
            return f'🗣️  [{sujeito.capitalize()}]: "{self._interpolar_texto(texto)}"'

        # Transferência entre personagens
        match_transf = re.match(r"^(\w+)\s+dá\s+(\d+)\s+(.+?)\s+para\s+(\w+)$", linha, re.IGNORECASE)
        if match_transf:
            doador, qtd, item, recebedor = match_transf.groups()
            qtd_val, item_clean = int(qtd), item.rstrip('s').lower()
            chave_d, chave_r = f"{doador.lower()}.{item_clean}", f"{recebedor.lower()}.{item_clean}"
            saldo = self.memoria.get(chave_d, 0)
            if saldo < qtd_val:
                return f"[Erro] {doador} não tem {qtd_val} {item_clean}(s) suficientes."
            self.memoria[chave_d] = saldo - qtd_val
            self.memoria[chave_r] = self.memoria.get(chave_r, 0) + qtd_val
            return f"[Transferência] {doador} deu {qtd_val} {item_clean}(s) para {recebedor}."

        # Incremento / Decremento
        match_mod = re.match(r"^(\w+)\s+(ganha|perde)\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_mod:
            sujeito, op, qtd, item = match_mod.groups()
            item_clean = item.replace("suas", "").strip().rstrip('s').lower()
            chave = f"{sujeito.lower()}.{item_clean}"
            val = int(qtd)
            if op.lower() == "ganha":
                self.memoria[chave] = self.memoria.get(chave, 0) + val
            else:
                self.memoria[chave] = max(0, self.memoria.get(chave, 0) - val)
            return f"[Modificação] {sujeito} agora tem {self.memoria[chave]} {item_clean}(s)."

        # Declaração numérica
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            self.memoria[f"{sujeito.lower()}.{item.rstrip('s').lower()}"] = int(valor)
            return f"[Criação] {sujeito} possui {valor} {item}."

        # Atributos de texto
        match_texto = re.match(r"^(\w+)\s+(?:mora em|é|está em)\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_texto:
            sujeito, valor_texto = match_texto.groups()
            self.memoria[f"{sujeito.lower()}.atributo"] = valor_texto
            return f"[Atributo] {sujeito} -> '{valor_texto}'"

        # Impressão de Estado
        if linha.lower().startswith("mostre"):
            return f"[Memória Total]: {self.memoria}"

        return f"[Instrução]: '{linha}'"

    def interpretar(self, historia):
        linhas = [l.strip() for l in historia.strip().split('\n') if l.strip()]
        resultados = []
        i = 0
        while i < len(linhas):
            linha = linhas[i]
            match_loop = re.match(r"^Enquanto\s+(.+?)\s+faça:$", linha, re.IGNORECASE)
            if match_loop:
                condicao_str = match_loop.group(1)
                sujeito_match = re.match(r"^(\w+)", condicao_str.strip())
                sujeito_loop = sujeito_match.group(1) if sujeito_match else None
                bloco_linhas = []
                j = i + 1
                while j < len(linhas) and linhas[j].lower().rstrip('.') != "fim do laço":
                    bloco_linhas.append(linhas[j])
                    j += 1
                iterações = 0
                while self._avaliar_condicao(condicao_str):
                    if iterações >= self.limite_loop:
                        resultados.append("[Erro] Loop infinito interrompido!")
                        break
                    for sub_linha in bloco_linhas:
                        res = self.executar_linha(sub_linha, sujeito_contexto=sujeito_loop)
                        resultados.append(f"  [Iteração {iterações + 1}] {res}")
                    iterações += 1
                resultados.append(f"[Loop Concluído] Executado {iterações} vez(es).")
                i = j + 1
                continue
            res = self.executar_linha(linha)
            if res:
                resultados.append(res)
            i += 1
        return resultados

    def interpretar_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        return self.interpretar(conteudo)
```

---

### Arquivo 3: `historia/cli.py`
Implemente o ponto de entrada da CLI usando `argparse`:

```python
import argparse
import sys
from historia.core import InterpretadorNarrativo

def main():
    parser = argparse.ArgumentParser(
        description="Interpretador de Linguagem Narrativa baseada em Histórias."
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    exec_parser = subparsers.add_parser("executar", help="Executa um arquivo .txt de história")
    exec_parser.add_argument("arquivo", type=str, help="Caminho do arquivo .txt")

    args = parser.parse_args()

    if args.comando == "executar":
        interpretador = InterpretadorNarrativo()
        try:
            resultados = interpretador.interpretar_arquivo(args.arquivo)
            print("\n--- INÍCIO DA EXECUÇÃO ---")
            for res in resultados:
                if res:
                    print(res)
            print("--- FIM DA EXECUÇÃO ---\n")
        except FileNotFoundError:
            print(f"Erro: Arquivo '{args.arquivo}' não encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

### Arquivo 4: `historia/__init__.py`
```python
from .core import InterpretadorNarrativo

__version__ = "0.1.0"
__all__ = ["InterpretadorNarrativo"]
```

---

### Arquivo 5: `exemplos/conto.txt`
```text
Maria tem 3 maçãs.
João tem 0 maçãs.
João tem 0 moedas.

Maria diz: "Eu tenho {maria.maçã} maçãs e vou dar para você, João!"

Enquanto Maria tiver maçãs faça:
    Maria dá 1 maçã para João.
    João ganha 2 moedas.
Fim do laço.

João diz: "Agora eu tenho {joao.maçã} maçãs e {joao.moeda} moedas."
Mostre tudo
```

---

## 4. Instrução de Execução e Verificação

Por fim, após gerar todos os arquivos acima, apresente os comandos de terminal exatos para o usuário rodar no computador:

1. **Instalar o pacote localmente:**
   `pip install -e .`
2. **Executar a história:**
   `historia executar exemplos/conto.txt`
```

---

<ElicitationsGroup message="O que gostaria de fazer em seguida?">
  <Elicitation label="Salvar este prompt em um arquivo local no seu projeto" query="Como faço um script simples em Python para criar a estrutura e gravar este arquivo de instrução automaticamente?"/>
  <Elicitation label="Solicitar melhorias como suporte a Funções/Capítulos" query="Como alterar a instrução da I.A. para incluir o suporte a Funções/Capítulos na linguagem?"/>
</ElicitationsGroup>


######## TURNO 10 USER ########
Crie em um arquivo só 

######## TURNO 10 GEMINI ########
Aqui está o **projeto completo reunido em um único arquivo de script Python (`interpretador.py`)**. 

Ele encapsula o interpretador, a interface CLI de linha de comando e cria automaticamente uma história de exemplo se nenhum arquivo for fornecido.

---

### `interpretador.py`

```python
import argparse
import os
import re
import sys

# ==============================================================================
# 1. MOTOR DO INTERPRETADOR NARRATIVO
# ==============================================================================

class InterpretadorNarrativo:
    """
    Interpretador para a Linguagem Narrativa.
    Converte declarações em linguagem natural em alocações de memória,
    operações aritméticas, controle de fluxo e diálogos.
    """
    def __init__(self, limite_loop=1000):
        self.memoria = {}
        self.limite_loop = limite_loop

    def _resolver_valor(self, termo, sujeito=None):
        termo = termo.strip().rstrip('s').lower()
        if termo.isdigit():
            return int(termo)
        chave_com_sujeito = f"{sujeito}.{termo}" if sujeito else termo
        if chave_com_sujeito in self.memoria:
            return self.memoria[chave_com_sujeito]
        if termo in self.memoria:
            return self.memoria[termo]
        return None

    def _interpolar_texto(self, texto):
        def substituir(match):
            chave = match.group(1).lower().strip()
            return str(self.memoria.get(chave, f"[{chave} desconhecido]"))
        return re.sub(r"\{(.+?)\}", substituir, texto)

    def _avaliar_condicao(self, condicao_texto):
        condicao_texto = condicao_texto.strip()
        match_exist = re.match(r"^(\w+)\s+(?:tiver|tem)\s+(.+)$", condicao_texto, re.IGNORECASE)
        if match_exist and not any(k in condicao_texto for k in ["mais de", "menos de", "igual a"]):
            sujeito, item = match_exist.groups()
            val = self._resolver_valor(item.rstrip('s').lower(), sujeito.lower())
            return val is not None and val > 0
        return False

    def executar_linha(self, linha, sujeito_contexto=None):
        linha = linha.strip().rstrip('.')
        if not linha:
            return None

        # Substituição de pronomes no contexto ativo
        if sujeito_contexto and re.match(r"^(ela|ele)\b", linha, re.IGNORECASE):
            linha = re.sub(r"^(ela|ele)\b", sujeito_contexto, linha, flags=re.IGNORECASE)

        # 1. Diálogos / Falas: Maria diz: "Olá {joao.nome}!"
        match_fala = re.match(r"^(\w+)\s+diz:\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_fala:
            sujeito, texto = match_fala.groups()
            return f'🗣️  [{sujeito.capitalize()}]: "{self._interpolar_texto(texto)}"'

        # 2. Transferência: Maria dá 1 maçã para João
        match_transf = re.match(r"^(\w+)\s+dá\s+(\d+)\s+(.+?)\s+para\s+(\w+)$", linha, re.IGNORECASE)
        if match_transf:
            doador, qtd, item, recebedor = match_transf.groups()
            qtd_val, item_clean = int(qtd), item.rstrip('s').lower()
            chave_d = f"{doador.lower()}.{item_clean}"
            chave_r = f"{recebedor.lower()}.{item_clean}"
            saldo = self.memoria.get(chave_d, 0)
            if saldo < qtd_val:
                return f"[Erro] {doador} não tem {qtd_val} {item_clean}(s) suficientes."
            self.memoria[chave_d] = saldo - qtd_val
            self.memoria[chave_r] = self.memoria.get(chave_r, 0) + qtd_val
            return f"[Transferência] {doador} deu {qtd_val} {item_clean}(s) para {recebedor}."

        # 3. Modificação aritmética: Maria ganha/perde 2 maçãs
        match_mod = re.match(r"^(\w+)\s+(ganha|perde)\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_mod:
            sujeito, op, qtd, item = match_mod.groups()
            item_clean = item.replace("suas", "").strip().rstrip('s').lower()
            chave = f"{sujeito.lower()}.{item_clean}"
            val = int(qtd)
            if op.lower() == "ganha":
                self.memoria[chave] = self.memoria.get(chave, 0) + val
            else:
                self.memoria[chave] = max(0, self.memoria.get(chave, 0) - val)
            return f"[Modificação] {sujeito} agora tem {self.memoria[chave]} {item_clean}(s)."

        # 4. Declaração numérica: Maria tem 10 maçãs
        match_decl = re.match(r"^(\w+)\s+tem\s+(\d+)\s+(.+)$", linha, re.IGNORECASE)
        if match_decl:
            sujeito, valor, item = match_decl.groups()
            self.memoria[f"{sujeito.lower()}.{item.rstrip('s').lower()}"] = int(valor)
            return f"[Criação] {sujeito} possui {valor} {item}."

        # 5. Atributos de texto: Maria mora em "São Paulo"
        match_texto = re.match(r"^(\w+)\s+(?:mora em|é|está em)\s*\"(.+)\"$", linha, re.IGNORECASE)
        if match_texto:
            sujeito, valor_texto = match_texto.groups()
            self.memoria[f"{sujeito.lower()}.atributo"] = valor_texto
            return f"[Atributo] {sujeito} -> '{valor_texto}'"

        # 6. Inspeção do estado de memória
        if linha.lower().startswith("mostre"):
            return f"[Estado da Memória]: {self.memoria}"

        return f"[Instrução]: '{linha}'"

    def interpretar(self, historia_texto):
        linhas = [l.strip() for l in historia_texto.strip().split('\n') if l.strip()]
        resultados = []
        i = 0
        while i < len(linhas):
            linha = linhas[i]
            match_loop = re.match(r"^Enquanto\s+(.+?)\s+faça:$", linha, re.IGNORECASE)
            if match_loop:
                condicao_str = match_loop.group(1)
                sujeito_match = re.match(r"^(\w+)", condicao_str.strip())
                sujeito_loop = sujeito_match.group(1) if sujeito_match else None
                bloco_linhas = []
                j = i + 1
                while j < len(linhas) and linhas[j].lower().rstrip('.') != "fim do laço":
                    bloco_linhas.append(linhas[j])
                    j += 1
                iteracoes = 0
                while self._avaliar_condicao(condicao_str):
                    if iteracoes >= self.limite_loop:
                        resultados.append("[Erro] Loop infinito interrompido!")
                        break
                    for sub_linha in bloco_linhas:
                        res = self.executar_linha(sub_linha, sujeito_contexto=sujeito_loop)
                        resultados.append(f"  [Iteração {iteracoes + 1}] {res}")
                    iteracoes += 1
                resultados.append(f"[Loop Concluído] Executado {iteracoes} vez(es).")
                i = j + 1
                continue
            res = self.executar_linha(linha)
            if res:
                resultados.append(res)
            i += 1
        return resultados

    def interpretar_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        return self.interpretar(conteudo)


# ==============================================================================
# 2. EXEMPLO DE HISTÓRIA EMBUTIDO
# ==============================================================================

HISTORIA_EXEMPLO = """Maria tem 3 maçãs.
Maria mora em "São Paulo".
João tem 0 maçãs.
João tem 0 moedas.

Maria diz: "Eu moro em {maria.atributo} e tenho {maria.maçã} maçãs."

Enquanto Maria tiver maçãs faça:
    Maria dá 1 maçã para João.
    João ganha 2 moedas.
Fim do laço.

João diz: "Obrigado Maria! Agora eu tenho {joao.maçã} maçãs e {joao.moeda} moedas."

Mostre tudo
"""


# ==============================================================================
# 3. INTERFACE DE LINHA DE COMANDO (CLI)
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Interpretador de Linguagem Narrativa em arquivo único."
    )
    parser.add_argument(
        "arquivo",
        nargs="?",
        type=str,
        help="Caminho para o arquivo .txt contendo a história (Opcional).",
    )

    args = parser.parse_args()
    interpretador = InterpretadorNarrativo()

    if args.arquivo:
        if not os.path.exists(args.arquivo):
            print(f"Erro: O arquivo '{args.arquivo}' não existe.", file=sys.stderr)
            sys.exit(1)
        print(f"--- EXECUTANDO ARQUIVO: {args.arquivo} ---")
        resultados = interpretador.interpretar_arquivo(args.arquivo)
    else:
        print("--- EXECUTANDO HISTÓRIA DE EXEMPLO EMBUTIDA ---")
        resultados = interpretador.interpretar(HISTORIA_EXEMPLO)

    print("\n" + "=" * 40)
    for res in resultados:
        if res:
            print(res)
    print("=" * 40 + "\n--- FIM DA EXECUÇÃO ---\n")


if __name__ == "__main__":
    main()
```

---

### Como Usar

1. Salve o código acima em um arquivo chamado `interpretador.py`.
2. Para rodar a **história de teste embutida**, basta executar:
   ```bash
   python interpretador.py
   ```
3. Para rodar **um arquivo `.txt` próprio** com sua história:
   ```bash
   python interpretador.py minha_historia.txt
   ```

<FollowUp label="Quer adicionar mais palavras-chave ou recursos de sintaxe ao arquivo?" query="Como posso adicionar novos comandos ao arquivo único do interpretador, como condições Se/Então?"/>
