from dataclasses import dataclass

from .erros import ErroSemantico
from .nos import (
    Capitulo, Chamada, Comparacao, ComparacaoEntre, Declaracao, DefinirTexto, E,
    Enquanto, Fala, Mostre, Nao, Narracao, Operacao, Ou, Pergunta, Referencia,
    Repita, Se, TextoIgual, Transferencia,
)

NUMERO, TEXTO = "quantidade", "texto"


@dataclass
class Diagnostico:
    nivel: str
    mensagem: str
    linha: int

    def __str__(self):
        icone = "❌ erro" if self.nivel == "erro" else "⚠️  aviso"
        return f"{icone} (linha {self.linha}): {self.mensagem}"


def _chave(sujeito, item):
    return (sujeito.chave, item.chave)


def _rotulo(sujeito, item):
    return f"'{item.exibicao}' de {sujeito.exibicao}"


class Analisador:
    def __init__(self):
        self.diagnosticos = []
        self.capitulos = {}
        self.escritas = {}
        self.leituras = []
        self.personagens = set()
        self.chamados = set()

    def erro(self, mensagem, linha):
        self.diagnosticos.append(Diagnostico("erro", mensagem, linha))

    def aviso(self, mensagem, linha):
        self.diagnosticos.append(Diagnostico("aviso", mensagem, linha))


    def analisar(self, programa):
        for no in programa.instrucoes:
            if isinstance(no, Capitulo):
                if no.nome.chave in self.capitulos:
                    anterior = self.capitulos[no.nome.chave].linha
                    self.erro(f"O capítulo '{no.nome.exibicao}' já foi definido na linha {anterior}", no.linha)
                else:
                    self.capitulos[no.nome.chave] = no
        self.visitar_bloco(programa.instrucoes)
        self.conferir_tipos_e_usos()
        for chave, cap in self.capitulos.items():
            if chave not in self.chamados:
                self.aviso(f"O capítulo '{cap.nome.exibicao}' nunca é contado", cap.linha)
        self.diagnosticos.sort(key=lambda d: (d.linha, d.nivel))
        return self.diagnosticos


    def escreve(self, sujeito, item, tipo, linha):
        self.personagens.add(sujeito.chave)
        self.escritas.setdefault(_chave(sujeito, item), {}).setdefault(tipo, (linha, sujeito, item))

    def le(self, sujeito, item, tipo, linha, exige_valor=True):
        self.leituras.append((sujeito, item, tipo, linha, exige_valor))

    def textos(self, texto):
        for parte in texto.partes:
            if isinstance(parte, Referencia):
                self.le(parte.sujeito, parte.item, None, parte.linha)


    def visitar_bloco(self, instrucoes):
        for no in instrucoes:
            self.visitar(no)

    def visitar(self, no):
        if isinstance(no, Declaracao):
            self.escreve(no.sujeito, no.item, NUMERO, no.linha)
        elif isinstance(no, DefinirTexto):
            self.textos(no.texto)
            self.escreve(no.sujeito, no.atributo, TEXTO, no.linha)
        elif isinstance(no, Operacao):
            if no.op == "/" and no.valor == 0:
                self.erro("Divisão por zero", no.linha)
            if no.op != "+":
                self.le(no.sujeito, no.item, NUMERO, no.linha)
            self.escreve(no.sujeito, no.item, NUMERO, no.linha)
        elif isinstance(no, Transferencia):
            if no.doador.chave == no.recebedor.chave:
                self.aviso(f"{no.doador.exibicao} dá {no.item.exibicao} para si mesmo(a)", no.linha)
            self.le(no.doador, no.item, NUMERO, no.linha)
            self.escreve(no.doador, no.item, NUMERO, no.linha)
            self.escreve(no.recebedor, no.item, NUMERO, no.linha)
        elif isinstance(no, (Fala, Narracao)):
            if isinstance(no, Fala):
                self.personagens.add(no.sujeito.chave)
            self.textos(no.texto)
        elif isinstance(no, Mostre):
            if no.sujeito is not None:
                self.leituras.append((no.sujeito, None, None, no.linha, False))
        elif isinstance(no, Pergunta):
            self.condicao(no.condicao)
        elif isinstance(no, Se):
            self.condicao(no.condicao)
            self.visitar_bloco(no.entao)
            self.visitar_bloco(no.senao)
        elif isinstance(no, Enquanto):
            self.condicao(no.condicao)
            self.visitar_bloco(no.corpo)
            lidas = self.chaves_condicao(no.condicao)
            if lidas and not (lidas & self.chaves_escritas(no.corpo, set())):
                self.aviso(
                    "Nada dentro deste laço muda a condição do 'Enquanto': possível laço infinito",
                    no.linha,
                )
        elif isinstance(no, Repita):
            if no.vezes == 0:
                self.aviso("'Repita 0 vezes' nunca executa o bloco", no.linha)
            self.visitar_bloco(no.corpo)
        elif isinstance(no, Capitulo):
            self.visitar_bloco(no.corpo)
        elif isinstance(no, Chamada):
            self.chamados.add(no.nome.chave)
            if no.nome.chave not in self.capitulos:
                self.erro(f"O capítulo '{no.nome.exibicao}' não foi definido", no.linha)

    def condicao(self, c):
        if isinstance(c, Comparacao):
            self.le(c.sujeito, c.item, NUMERO, c.linha, exige_valor=False)
        elif isinstance(c, ComparacaoEntre):
            self.le(c.sujeito, c.item, NUMERO, c.linha, exige_valor=False)
            self.le(c.outro, c.item, NUMERO, c.linha, exige_valor=False)
        elif isinstance(c, TextoIgual):
            self.le(c.sujeito, c.atributo, TEXTO, c.linha, exige_valor=False)
        elif isinstance(c, Nao):
            self.condicao(c.condicao)
        elif isinstance(c, (E, Ou)):
            self.condicao(c.esquerda)
            self.condicao(c.direita)


    def conferir_tipos_e_usos(self):
        for (s, i), tipos in self.escritas.items():
            if len(tipos) > 1:
                linha, sujeito, item = max(tipos.values(), key=lambda t: t[0])
                self.erro(f"{_rotulo(sujeito, item)} é usado como texto e como quantidade", linha)

        avisados = set()
        for sujeito, item, tipo, linha, exige_valor in self.leituras:
            if item is None:
                if sujeito.chave not in self.personagens:
                    self.aviso(f"{sujeito.exibicao} não aparece em nenhum outro lugar da história", linha)
                continue
            tipos = self.escritas.get(_chave(sujeito, item), {})
            if not tipos:
                if exige_valor and (sujeito.chave, item.chave) not in avisados:
                    avisados.add((sujeito.chave, item.chave))
                    self.aviso(f"{_rotulo(sujeito, item)} é usado mas nunca recebe um valor", linha)
                continue
            if tipo is not None and tipo not in tipos and len(tipos) == 1:
                definido = next(iter(tipos))
                self.erro(f"{_rotulo(sujeito, item)} é um(a) {definido}, mas aqui é usado como {tipo}", linha)

    def chaves_condicao(self, c):
        if isinstance(c, (Comparacao, TextoIgual)):
            item = c.item if isinstance(c, Comparacao) else c.atributo
            return {_chave(c.sujeito, item)}
        if isinstance(c, ComparacaoEntre):
            return {_chave(c.sujeito, c.item), _chave(c.outro, c.item)}
        if isinstance(c, Nao):
            return self.chaves_condicao(c.condicao)
        if isinstance(c, (E, Ou)):
            return self.chaves_condicao(c.esquerda) | self.chaves_condicao(c.direita)
        return set()

    def chaves_escritas(self, instrucoes, visitados):
        escritas = set()
        for no in instrucoes:
            if isinstance(no, (Declaracao, Operacao)):
                escritas.add(_chave(no.sujeito, no.item))
            elif isinstance(no, DefinirTexto):
                escritas.add(_chave(no.sujeito, no.atributo))
            elif isinstance(no, Transferencia):
                escritas |= {_chave(no.doador, no.item), _chave(no.recebedor, no.item)}
            elif isinstance(no, Se):
                escritas |= self.chaves_escritas(no.entao, visitados)
                escritas |= self.chaves_escritas(no.senao, visitados)
            elif isinstance(no, (Enquanto, Repita)):
                escritas |= self.chaves_escritas(no.corpo, visitados)
            elif isinstance(no, Chamada) and no.nome.chave not in visitados:
                capitulo = self.capitulos.get(no.nome.chave)
                if capitulo is not None:
                    escritas |= self.chaves_escritas(capitulo.corpo, visitados | {no.nome.chave})
        return escritas


def analisar_semantica(programa):
    return Analisador().analisar(programa)


def exigir_sem_erros(diagnosticos):
    for d in diagnosticos:
        if d.nivel == "erro":
            raise ErroSemantico(d.mensagem, d.linha)
