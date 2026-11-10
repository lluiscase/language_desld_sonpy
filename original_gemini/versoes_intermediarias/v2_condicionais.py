# Turno 2 da conversa com o Gemini (extraido sem alteracoes)
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


if __name__ == "__main__":
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
