from dataclasses import dataclass, fields, is_dataclass
from typing import List, NamedTuple, Optional, Union


class Nome(NamedTuple):
    chave: str
    exibicao: str


@dataclass
class Referencia:
    linha: int
    sujeito: Nome
    item: Nome


@dataclass
class Texto:
    linha: int
    partes: List[Union[str, Referencia]]


@dataclass
class Comparacao:
    linha: int
    sujeito: Nome
    item: Nome
    op: str
    valor: int


@dataclass
class ComparacaoEntre:
    linha: int
    sujeito: Nome
    outro: Nome
    item: Nome
    op: str


@dataclass
class TextoIgual:
    linha: int
    sujeito: Nome
    atributo: Nome
    texto: str


@dataclass
class Nao:
    linha: int
    condicao: object


@dataclass
class E:
    linha: int
    esquerda: object
    direita: object


@dataclass
class Ou:
    linha: int
    esquerda: object
    direita: object


@dataclass
class Declaracao:
    linha: int
    sujeito: Nome
    item: Nome
    valor: int


@dataclass
class DefinirTexto:
    linha: int
    sujeito: Nome
    atributo: Nome
    texto: Texto


@dataclass
class Operacao:
    linha: int
    sujeito: Nome
    item: Nome
    op: str
    valor: Optional[int]


@dataclass
class Transferencia:
    linha: int
    doador: Nome
    recebedor: Nome
    item: Nome
    valor: Optional[int]


@dataclass
class Fala:
    linha: int
    sujeito: Nome
    verbo: str
    texto: Texto


@dataclass
class Narracao:
    linha: int
    texto: Texto


@dataclass
class Mostre:
    linha: int
    sujeito: Optional[Nome]


@dataclass
class Pergunta:
    linha: int
    condicao: object
    texto: str


@dataclass
class Se:
    linha: int
    condicao: object
    entao: list
    senao: list


@dataclass
class Enquanto:
    linha: int
    condicao: object
    corpo: list


@dataclass
class Repita:
    linha: int
    vezes: int
    corpo: list


@dataclass
class Capitulo:
    linha: int
    nome: Nome
    corpo: list


@dataclass
class Chamada:
    linha: int
    nome: Nome


@dataclass
class Programa:
    linha: int
    instrucoes: list


def formatar_ast(no, nivel=0):
    recuo = "  " * nivel
    if isinstance(no, Nome):
        return f"{no.exibicao}"
    if isinstance(no, list):
        if not no:
            return "[]"
        return "\n" + "\n".join(f"{recuo}- " + formatar_ast(x, nivel + 1).lstrip() for x in no)
    if not is_dataclass(no):
        return repr(no)
    partes = []
    for f in fields(no):
        if f.name == "linha":
            continue
        valor = getattr(no, f.name)
        texto = formatar_ast(valor, nivel + 1)
        partes.append(f"{recuo}  {f.name}: {texto}")
    return f"{type(no).__name__} (linha {no.linha})\n" + "\n".join(partes)
