# Turno 1 da conversa com o Gemini (extraido sem alteracoes)
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


if __name__ == "__main__":
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
