from pathlib import Path

from .nos import (
    Capitulo, Comparacao, ComparacaoEntre, E, Nao, Ou, TextoIgual,
)
from .runtime import LIMITE_LACO_PADRAO

RUNTIME = Path(__file__).with_name("runtime.py")


def _tupla(nome):
    return repr(tuple(nome))


def _partes(texto):
    partes = [p if isinstance(p, str) else (tuple(p.sujeito), tuple(p.item)) for p in texto.partes]
    return repr(partes)


def _nome_funcao(nome):
    return "capitulo_" + "".join(c if c.isalnum() else "_" for c in nome.chave)


class GeradorPython:
    def __init__(self):
        self.linhas = []
        self.nivel = 0
        self.contador_lacos = 0

    def emitir(self, codigo=""):
        self.linhas.append(("    " * self.nivel + codigo) if codigo else "")

    def gerar(self, programa, origem="<história>", limite_laco=LIMITE_LACO_PADRAO):
        self.emitir(f"# Gerado pelo compilador da Linguagem Narrativa a partir de: {origem}")
        self.emitir("# Não edite: altere a história e compile de novo.")
        self.emitir("import sys")
        self.emitir()
        self.emitir("# " + "-" * 30 + " runtime " + "-" * 30)
        self.linhas.extend(RUNTIME.read_text(encoding="utf-8").splitlines())
        self.emitir("# " + "-" * 30 + " história " + "-" * 30)
        self.emitir()
        self.emitir()
        self.emitir("class ErroExecucao(Exception):")
        self.emitir("    def __init__(self, mensagem, linha=None):")
        self.emitir("        super().__init__(mensagem)")
        self.emitir("        self.linha = linha")
        self.emitir()
        self.emitir()
        self.emitir(f"m = Memoria(ErroExecucao, limite_laco={limite_laco!r})")
        self.emitir()

        for no in programa.instrucoes:
            if isinstance(no, Capitulo):
                self.emitir()
                self.emitir(f"def {_nome_funcao(no.nome)}():  # linha {no.linha}")
                self.corpo(no.corpo)
                self.emitir()

        self.emitir()
        self.emitir("def historia():")
        self.corpo([no for no in programa.instrucoes if not isinstance(no, Capitulo)])
        self.emitir()
        self.emitir()
        self.emitir('if __name__ == "__main__":')
        self.emitir('    if hasattr(sys.stdout, "reconfigure"):')
        self.emitir('        sys.stdout.reconfigure(encoding="utf-8", errors="replace")')
        self.emitir("    try:")
        self.emitir("        historia()")
        self.emitir("    except ErroExecucao as erro:")
        self.emitir('        print(f"Erro de execução na linha {erro.linha}: {erro}", file=sys.stderr)')
        self.emitir("        sys.exit(1)")
        return "\n".join(self.linhas) + "\n"


    def corpo(self, instrucoes):
        self.nivel += 1
        if not instrucoes:
            self.emitir("pass")
        for no in instrucoes:
            getattr(self, "_" + type(no).__name__)(no)
        self.nivel -= 1

    def _Declaracao(self, no):
        self.emitir(f"m.declarar({_tupla(no.sujeito)}, {_tupla(no.item)}, {no.valor!r}, {no.linha})")

    def _DefinirTexto(self, no):
        texto = f"m.interpolar({_partes(no.texto)}, {no.linha})"
        self.emitir(f"m.definir_texto({_tupla(no.sujeito)}, {_tupla(no.atributo)}, {texto}, {no.linha})")

    def _Operacao(self, no):
        self.emitir(
            f"m.operar({_tupla(no.sujeito)}, {_tupla(no.item)}, {no.op!r}, {no.valor!r}, {no.linha})")

    def _Transferencia(self, no):
        self.emitir(
            f"m.transferir({_tupla(no.doador)}, {_tupla(no.recebedor)}, {_tupla(no.item)}, "
            f"{no.valor!r}, {no.linha})")

    def _Fala(self, no):
        self.emitir(
            f"print(m.fala({_tupla(no.sujeito)}, {no.verbo!r}, {_partes(no.texto)}, {no.linha}))")

    def _Narracao(self, no):
        self.emitir(f"print(m.narrar({_partes(no.texto)}, {no.linha}))")

    def _Mostre(self, no):
        alvo = _tupla(no.sujeito) if no.sujeito else "None"
        self.emitir(f"print(m.mostrar({alvo}))")

    def _Pergunta(self, no):
        self.emitir(f"print(m.perguntar({no.texto!r}, {self.condicao(no.condicao)}))")

    def _Se(self, no):
        self.emitir(f"if {self.condicao(no.condicao)}:  # linha {no.linha}")
        self.corpo(no.entao)
        if no.senao:
            self.emitir("else:")
            self.corpo(no.senao)

    def _Enquanto(self, no):
        self.contador_lacos += 1
        contador = f"_voltas{self.contador_lacos}"
        self.emitir(f"{contador} = 0")
        self.emitir(f"while {self.condicao(no.condicao)}:  # linha {no.linha}")
        self.nivel += 1
        self.emitir(f"{contador} += 1")
        self.emitir(f"m.passo_laco({contador}, {no.linha})")
        self.nivel -= 1
        self.corpo(no.corpo)

    def _Repita(self, no):
        self.emitir(f"for _ in range({no.vezes}):  # linha {no.linha}")
        self.corpo(no.corpo)

    def _Chamada(self, no):
        self.emitir(f"m.entrar({no.nome.exibicao!r}, {no.linha})")
        self.emitir("try:")
        self.nivel += 1
        self.emitir(f"{_nome_funcao(no.nome)}()")
        self.nivel -= 1
        self.emitir("finally:")
        self.nivel += 1
        self.emitir("m.sair()")
        self.nivel -= 1


    def condicao(self, c):
        if isinstance(c, Comparacao):
            return f"m.comparar({_tupla(c.sujeito)}, {_tupla(c.item)}, {c.op!r}, {c.valor!r}, {c.linha})"
        if isinstance(c, ComparacaoEntre):
            return (f"m.comparar_entre({_tupla(c.sujeito)}, {_tupla(c.outro)}, {_tupla(c.item)}, "
                    f"{c.op!r}, {c.linha})")
        if isinstance(c, TextoIgual):
            return f"m.texto_igual({_tupla(c.sujeito)}, {_tupla(c.atributo)}, {c.texto!r}, {c.linha})"
        if isinstance(c, Nao):
            return f"(not {self.condicao(c.condicao)})"
        if isinstance(c, E):
            return f"({self.condicao(c.esquerda)} and {self.condicao(c.direita)})"
        if isinstance(c, Ou):
            return f"({self.condicao(c.esquerda)} or {self.condicao(c.direita)})"
        raise TypeError(f"Condição desconhecida: {type(c).__name__}")


def gerar_python(programa, origem="<história>", limite_laco=LIMITE_LACO_PADRAO):
    return GeradorPython().gerar(programa, origem, limite_laco)
