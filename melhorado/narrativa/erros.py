class ErroNarrativo(Exception):
    fase = "Erro"

    def __init__(self, mensagem, linha=None, coluna=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna

    def formatar(self, fonte=None):
        onde = ""
        if self.linha is not None:
            onde = f" na linha {self.linha}"
            if self.coluna is not None:
                onde += f", coluna {self.coluna}"
        texto = f"{self.fase}{onde}: {self.mensagem}"
        if fonte is not None and self.linha is not None:
            linhas = fonte.splitlines()
            if 1 <= self.linha <= len(linhas):
                margem = f"{self.linha:>4} | "
                texto += f"\n{margem}{linhas[self.linha - 1]}"
                if self.coluna is not None:
                    texto += "\n" + " " * (len(margem) - 2) + "| " + " " * (self.coluna - 1) + "^"
        return texto


class ErroLexico(ErroNarrativo):
    fase = "Erro léxico"


class ErroSintatico(ErroNarrativo):
    fase = "Erro de sintaxe"


class ErroSemantico(ErroNarrativo):
    fase = "Erro semântico"


class ErroExecucao(ErroNarrativo):
    fase = "Erro de execução"
