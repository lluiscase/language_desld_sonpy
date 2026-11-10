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
