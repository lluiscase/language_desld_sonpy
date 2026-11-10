# Turno 0 da conversa com o Gemini (extraido sem alteracoes)
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
