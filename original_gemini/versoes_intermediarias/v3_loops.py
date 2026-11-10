# Turno 3 da conversa com o Gemini (extraido sem alteracoes)
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


if __name__ == "__main__":
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
