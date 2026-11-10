# Turno 5 da conversa com o Gemini (extraido sem alteracoes)
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


if __name__ == "__main__":
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
