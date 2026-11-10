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
