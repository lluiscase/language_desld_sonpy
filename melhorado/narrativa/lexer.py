from dataclasses import dataclass, field

from .erros import ErroLexico
from .texto import normalizar

PALAVRA = "PALAVRA"
NUMERO = "NUMERO"
TEXTO = "TEXTO"
PONTO = "PONTO"
VIRGULA = "VIRGULA"
DOIS_PONTOS = "DOIS_PONTOS"
INTERROGACAO = "INTERROGACAO"
NOVA_LINHA = "NOVA_LINHA"
FIM = "FIM"

_SIMBOLOS = {
    ".": PONTO,
    "!": PONTO,
    ";": PONTO,
    ",": VIRGULA,
    ":": DOIS_PONTOS,
    "?": INTERROGACAO,
}
_ASPAS = {'"': '"', "“": "”"}


@dataclass(frozen=True)
class Token:
    tipo: str
    valor: object
    linha: int
    coluna: int
    inicio: int
    fim: int
    norm: str = field(default=None, compare=False)

    def __repr__(self):
        return f"Token({self.tipo}, {self.valor!r}, {self.linha}:{self.coluna})"


def tokenizar(fonte):
    tokens = []
    i, linha, inicio_linha, n = 0, 1, 0, len(fonte)

    def novo(tipo, valor, ini, fim):
        norm = normalizar(valor) if tipo == PALAVRA else None
        tokens.append(Token(tipo, valor, linha, ini - inicio_linha + 1, ini, fim, norm))

    while i < n:
        c = fonte[i]
        if c == "\n":
            novo(NOVA_LINHA, "\n", i, i + 1)
            i += 1
            linha += 1
            inicio_linha = i
        elif c in " \t\r﻿":
            i += 1
        elif c == "#":
            while i < n and fonte[i] != "\n":
                i += 1
        elif c in _ASPAS:
            fecha = _ASPAS[c]
            j = i + 1
            while j < n and fonte[j] != fecha and fonte[j] != "\n":
                j += 1
            if j >= n or fonte[j] == "\n":
                raise ErroLexico("Texto sem aspas de fechamento", linha, i - inicio_linha + 1)
            novo(TEXTO, fonte[i + 1 : j], i, j + 1)
            i = j + 1
        elif "0" <= c <= "9":
            j = i
            while j < n and "0" <= fonte[j] <= "9":
                j += 1
            novo(NUMERO, int(fonte[i:j]), i, j)
            i = j
        elif c.isalpha() or c == "_":
            j = i + 1
            while j < n and (
                fonte[j].isalnum()
                or fonte[j] == "_"
                or (fonte[j] == "-" and j + 1 < n and fonte[j + 1].isalpha())
            ):
                j += 1
            novo(PALAVRA, fonte[i:j], i, j)
            i = j
        elif c in _SIMBOLOS:
            novo(_SIMBOLOS[c], c, i, i + 1)
            i += 1
        else:
            raise ErroLexico(f"Caractere inesperado {c!r}", linha, i - inicio_linha + 1)

    novo(FIM, None, n, n)
    return tokens
