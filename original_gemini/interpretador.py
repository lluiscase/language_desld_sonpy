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
