from .erros import ErroExecucao, ErroLexico, ErroNarrativo, ErroSemantico, ErroSintatico
from .gerador import gerar_python
from .interpretador import Interpretador
from .lexer import tokenizar
from .parser import Parser, analisar_sintaxe
from .runtime import LIMITE_LACO_PADRAO
from .semantica import Diagnostico, analisar_semantica, exigir_sem_erros

__version__ = "0.2.0"


def analisar(fonte):
    programa = analisar_sintaxe(tokenizar(fonte), fonte)
    diagnosticos = analisar_semantica(programa)
    exigir_sem_erros(diagnosticos)
    return programa, diagnosticos


def executar(fonte, limite_laco=LIMITE_LACO_PADRAO, rastrear=False):
    programa, _ = analisar(fonte)
    saida = []
    Interpretador(saida.append, limite_laco, rastrear).executar(programa)
    return saida


def compilar(fonte, origem="<história>", limite_laco=LIMITE_LACO_PADRAO):
    programa, _ = analisar(fonte)
    return gerar_python(programa, origem, limite_laco)


class InterpretadorNarrativo:
    def __init__(self, limite_loop=LIMITE_LACO_PADRAO):
        self._saida = []
        self._interp = Interpretador(self._saida.append, limite_loop)
        self._ultimo_sujeito = None

    @property
    def memoria(self):
        return self._interp.memoria.memoria_plana()

    def interpretar(self, historia):
        parser = Parser(tokenizar(historia), historia, self._ultimo_sujeito)
        programa = parser.programa()
        self._ultimo_sujeito = parser.ultimo_sujeito
        self._saida.clear()
        self._interp.executar(programa)
        return list(self._saida)

    def interpretar_arquivo(self, caminho):
        with open(caminho, encoding="utf-8") as f:
            return self.interpretar(f.read())


__all__ = [
    "analisar", "executar", "compilar", "tokenizar", "analisar_sintaxe",
    "analisar_semantica", "gerar_python", "Interpretador", "InterpretadorNarrativo",
    "Diagnostico", "ErroNarrativo", "ErroLexico", "ErroSintatico", "ErroSemantico",
    "ErroExecucao",
]
