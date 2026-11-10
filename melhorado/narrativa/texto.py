import re
import unicodedata

VOGAIS = "aeiouáéíóúâêôãõ"

_PLURAIS = [
    ("ões", "ão", 4), ("ães", "ão", 4), ("ãos", "ão", 4),
    ("ais", "al", 5), ("éis", "el", 5), ("óis", "ol", 5),
    ("ns", "m", 4),
]
_INVARIAVEIS = ("is", "us", "ss")


def sem_acentos(texto):
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def normalizar(texto):
    return sem_acentos(texto).lower()


def singular(palavra):
    p = palavra.lower()
    for sufixo, troca, minimo in _PLURAIS:
        if p.endswith(sufixo) and len(p) >= minimo:
            return p[: -len(sufixo)] + troca
    if len(p) > 4 and p[-3:] in ("res", "zes", "ses") and p[-4] in VOGAIS:
        return p[:-2]
    curta_em_is = len(p) <= 4 and p.endswith("is")
    if len(p) > 2 and p.endswith("s") and (curta_em_is or not normalizar(p).endswith(_INVARIAVEIS)):
        return p[:-1]
    return p


def chave_personagem(nome):
    return normalizar(nome.strip())


def chave_item(palavras):
    singulares = [singular(p) for p in palavras]
    return "_".join(normalizar(p) for p in singulares), " ".join(singulares)


def chave_capitulo(palavras):
    return "_".join(normalizar(p) for p in palavras)


def separar_palavras_item(texto):
    return [p for p in re.split(r"[\s_]+", texto.strip()) if p]
