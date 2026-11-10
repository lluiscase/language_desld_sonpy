from .erros import ErroExecucao
from .nos import (
    Capitulo, Comparacao, ComparacaoEntre, E, Nao, Ou, TextoIgual,
)
from .runtime import LIMITE_LACO_PADRAO, Memoria


def _partes(texto):
    return [p if isinstance(p, str) else (tuple(p.sujeito), tuple(p.item)) for p in texto.partes]


class Interpretador:
    def __init__(self, saida=print, limite_laco=LIMITE_LACO_PADRAO, rastrear=False):
        self.memoria = Memoria(ErroExecucao, limite_laco)
        self.saida = saida
        self.rastrear = rastrear
        self.capitulos = {}

    def executar(self, programa):
        for no in programa.instrucoes:
            if isinstance(no, Capitulo):
                self.capitulos[no.nome.chave] = no
        self.bloco(programa.instrucoes)

    def bloco(self, instrucoes):
        for no in instrucoes:
            getattr(self, "_" + type(no).__name__)(no)

    def _rastro(self, no, sujeito):
        if self.rastrear:
            self.saida(f"   · linha {no.linha}: {self.memoria.mostrar(tuple(sujeito))[2:]}")


    def _Declaracao(self, no):
        self.memoria.declarar(no.sujeito, no.item, no.valor, no.linha)
        self._rastro(no, no.sujeito)

    def _DefinirTexto(self, no):
        texto = self.memoria.interpolar(_partes(no.texto), no.linha)
        self.memoria.definir_texto(no.sujeito, no.atributo, texto, no.linha)
        self._rastro(no, no.sujeito)

    def _Operacao(self, no):
        self.memoria.operar(no.sujeito, no.item, no.op, no.valor, no.linha)
        self._rastro(no, no.sujeito)

    def _Transferencia(self, no):
        self.memoria.transferir(no.doador, no.recebedor, no.item, no.valor, no.linha)
        self._rastro(no, no.doador)
        self._rastro(no, no.recebedor)

    def _Fala(self, no):
        self.saida(self.memoria.fala(no.sujeito, no.verbo, _partes(no.texto), no.linha))

    def _Narracao(self, no):
        self.saida(self.memoria.narrar(_partes(no.texto), no.linha))

    def _Mostre(self, no):
        self.saida(self.memoria.mostrar(tuple(no.sujeito) if no.sujeito else None))

    def _Pergunta(self, no):
        self.saida(self.memoria.perguntar(no.texto, self.condicao(no.condicao)))

    def _Se(self, no):
        self.bloco(no.entao if self.condicao(no.condicao) else no.senao)

    def _Enquanto(self, no):
        contador = 0
        while self.condicao(no.condicao):
            contador += 1
            self.memoria.passo_laco(contador, no.linha)
            self.bloco(no.corpo)

    def _Repita(self, no):
        for _ in range(no.vezes):
            self.bloco(no.corpo)

    def _Capitulo(self, no):
        pass

    def _Chamada(self, no):
        capitulo = self.capitulos.get(no.nome.chave)
        if capitulo is None:
            raise ErroExecucao(f"O capítulo '{no.nome.exibicao}' não existe", no.linha)
        self.memoria.entrar(no.nome.exibicao, no.linha)
        try:
            self.bloco(capitulo.corpo)
        finally:
            self.memoria.sair()


    def condicao(self, c):
        m = self.memoria
        if isinstance(c, Comparacao):
            return m.comparar(c.sujeito, c.item, c.op, c.valor, c.linha)
        if isinstance(c, ComparacaoEntre):
            return m.comparar_entre(c.sujeito, c.outro, c.item, c.op, c.linha)
        if isinstance(c, TextoIgual):
            return m.texto_igual(c.sujeito, c.atributo, c.texto, c.linha)
        if isinstance(c, Nao):
            return not self.condicao(c.condicao)
        if isinstance(c, E):
            return self.condicao(c.esquerda) and self.condicao(c.direita)
        if isinstance(c, Ou):
            return self.condicao(c.esquerda) or self.condicao(c.direita)
        raise ErroExecucao(f"Condição desconhecida: {type(c).__name__}", getattr(c, "linha", None))
