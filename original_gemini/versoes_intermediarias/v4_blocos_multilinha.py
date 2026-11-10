# Turno 4 da conversa com o Gemini (extraido sem alteracoes)
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


if __name__ == "__main__":
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
