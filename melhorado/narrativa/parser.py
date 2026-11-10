from .erros import ErroSintatico
from .lexer import (
    DOIS_PONTOS, FIM, INTERROGACAO, NOVA_LINHA, NUMERO, PALAVRA, PONTO, TEXTO, VIRGULA,
)
from .nos import (
    Capitulo, Chamada, Comparacao, ComparacaoEntre, Declaracao, DefinirTexto, E,
    Enquanto, Fala, Mostre, Nao, Narracao, Nome, Operacao, Ou, Pergunta, Programa,
    Referencia, Repita, Se, Texto, TextoIgual, Transferencia,
)
from .texto import (
    chave_capitulo, chave_item, chave_personagem, normalizar, separar_palavras_item,
)

EXTENSO = {
    "zero": 0, "nenhum": 0, "nenhuma": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2,
    "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9,
    "dez": 10, "onze": 11, "doze": 12, "vinte": 20, "trinta": 30, "cem": 100, "mil": 1000,
}
PRONOMES = {"ela", "ele"}
TODOS = {"todas", "todos"}
POSSESSIVOS = {"suas", "seus", "sua", "seu", "as", "os"}
PARADAS_ITEM = {
    "para", "pra", "ao", "aos", "a", "que", "do", "quanto", "entao", "faca",
    "e", "ou", "ela", "ele", "senao", "por",
}
RESERVADAS = {
    "se", "senao", "entao", "enquanto", "faca", "repita", "vezes", "fim", "capitulo",
    "mostre", "conte", "leia", "narrador", "e", "ou", "nao", "tudo",
}

VERBOS_GANHAR = {"ganha", "recebe", "compra", "colhe", "encontra", "acha"}
VERBOS_PERDER = {"perde", "gasta", "come", "vende", "usa", "bebe"}
VERBOS_DAR = {"da", "entrega", "passa", "empresta", "oferece"}
VERBOS_FALA = {"diz", "fala", "pergunta", "responde", "grita", "sussurra", "pensa", "conta"}
VERBOS_TER = {"tem", "possui"}
OPS_IMPLICITAS = {"vezes": "*", "mais": "+", "menos": "-", "dividido": "/"}

TIPO_DO_FIM = {
    "se": "se", "condicao": "se",
    "laco": "enquanto", "enquanto": "enquanto",
    "repeticao": "repita", "repita": "repita",
    "capitulo": "capitulo",
}
FECHAMENTO = {
    "se": "Fim do se", "enquanto": "Fim do laço",
    "repita": "Fim da repetição", "capitulo": "Fim do capítulo",
}

NOME_TOKEN = {
    NOVA_LINHA: "quebra de linha", FIM: "fim da história", PONTO: "'.'",
    VIRGULA: "','", DOIS_PONTOS: "':'", INTERROGACAO: "'?'",
}


class Parser:
    def __init__(self, tokens, fonte, ultimo_sujeito=None):
        self.tokens = tokens
        self.fonte = fonte
        self.i = 0
        self.recentes = [ultimo_sujeito] if ultimo_sujeito else []


    def atual(self, k=0):
        return self.tokens[min(self.i + k, len(self.tokens) - 1)]

    def avancar(self):
        tok = self.atual()
        if tok.tipo != FIM:
            self.i += 1
        return tok

    def eh(self, *palavras, k=0):
        for desloc, esperado in enumerate(palavras):
            tok = self.atual(k + desloc)
            opcoes = esperado if isinstance(esperado, (set, frozenset, tuple)) else {esperado}
            if tok.tipo != PALAVRA or tok.norm not in opcoes:
                return False
        return True

    def aceitar(self, *palavras):
        if self.eh(*palavras):
            for _ in palavras:
                self.avancar()
            return True
        return False

    def esperar_palavra(self, *palavras, descricao):
        if not self.aceitar(*palavras):
            self.erro(f"Esperava '{descricao}'")

    def esperar(self, tipo, descricao):
        if self.atual().tipo != tipo:
            self.erro(f"Esperava {descricao}")
        return self.avancar()

    def descrever(self, tok):
        if tok.tipo in NOME_TOKEN:
            return NOME_TOKEN[tok.tipo]
        if tok.tipo == TEXTO:
            return f'o texto "{tok.valor}"'
        return f"'{tok.valor}'"

    def erro(self, mensagem, tok=None, mostrar_encontrado=True):
        tok = tok or self.atual()
        if mostrar_encontrado:
            mensagem += f", mas encontrei {self.descrever(tok)}"
        raise ErroSintatico(mensagem, tok.linha, tok.coluna)

    def pular_separadores(self):
        while self.atual().tipo in (NOVA_LINHA, PONTO, VIRGULA):
            self.avancar()

    def fim_de_instrucao(self):
        tok = self.atual()
        if tok.tipo in (PONTO, VIRGULA, NOVA_LINHA, FIM) or self.eh("senao"):
            return
        self.erro("Esperava o fim da frase (um '.' ou quebra de linha)")

    def inicio_quantidade(self, k=0, permitir_tudo=False):
        tok = self.atual(k)
        if tok.tipo == NUMERO:
            return True
        if tok.tipo == PALAVRA and tok.norm in EXTENSO:
            return True
        return permitir_tudo and self.eh(TODOS, k=k)


    def programa(self):
        instrucoes = []
        self.pular_separadores()
        while self.atual().tipo != FIM:
            instrucoes.extend(self.instrucao(topo=True))
            self.pular_separadores()
        return Programa(1, instrucoes)

    def instrucao(self, topo=False):
        tok = self.atual()
        if self.eh("se"):
            return [self.se()]
        if self.eh("enquanto"):
            return [self.enquanto()]
        if self.eh("repita"):
            return [self.repita()]
        if self.eh("capitulo"):
            if not topo:
                self.erro("Capítulos só podem ser definidos fora de outros blocos", mostrar_encontrado=False)
            return [self.capitulo()]
        if self.eh("fim") or self.eh("senao"):
            self.erro(f"'{tok.valor}' sem um bloco aberto correspondente", mostrar_encontrado=False)
        resultado = self.sequencia_simples()
        self.fim_de_instrucao()
        return resultado

    def sequencia_simples(self):
        resultado = self.simples()
        while self.eh("e"):
            self.avancar()
            resultado.extend(self.simples())
        return resultado

    def abrir_bloco(self):
        self.aceitar_simbolo(DOIS_PONTOS)
        return self.atual().tipo in (NOVA_LINHA, FIM)

    def aceitar_simbolo(self, tipo):
        if self.atual().tipo == tipo:
            self.avancar()
            return True
        return False

    def bloco(self, tipo, tok_abertura, permitir_senao=False):
        corpo = []
        while True:
            self.pular_separadores()
            tok = self.atual()
            if tok.tipo == FIM:
                self.erro(
                    f"O bloco '{tok_abertura.valor}' aberto na linha {tok_abertura.linha} "
                    f"não foi fechado com '{FECHAMENTO[tipo]}'",
                    tok, mostrar_encontrado=False,
                )
            if self.eh("fim"):
                self.fechar(tipo, tok_abertura)
                return corpo, False
            if permitir_senao and self.eh("senao"):
                return corpo, True
            corpo.extend(self.instrucao())

    def fechar(self, tipo, tok_abertura):
        tok_fim = self.avancar()
        while self.atual().tipo == PALAVRA:
            palavra = self.avancar()
            outro = TIPO_DO_FIM.get(palavra.norm)
            if outro is not None and outro != tipo:
                self.erro(
                    f"Esperava '{FECHAMENTO[tipo]}' para fechar o bloco da linha "
                    f"{tok_abertura.linha}, mas encontrei '{FECHAMENTO[outro]}'",
                    tok_fim, mostrar_encontrado=False,
                )
        self.fim_de_instrucao()


    def se(self):
        tok = self.avancar()
        cond = self.condicao()
        if not self.aceitar("entao") and self.atual().tipo != DOIS_PONTOS:
            self.erro("Esperava 'então' depois da condição do 'Se'")
        if self.abrir_bloco():
            return self._se_bloco(tok, cond)
        entao = self.sequencia_simples()
        senao = []
        if self.atual().tipo == VIRGULA and self.eh("senao", k=1):
            self.avancar()
        if self.aceitar("senao"):
            self.aceitar_simbolo(DOIS_PONTOS)
            senao = self.sequencia_simples()
        self.fim_de_instrucao()
        return Se(tok.linha, cond, entao, senao)

    def _se_bloco(self, tok_se, cond):
        entao, tem_senao = self.bloco("se", tok_se, permitir_senao=True)
        senao = []
        if tem_senao:
            self.avancar()
            if self.eh("se"):
                tok2 = self.avancar()
                cond2 = self.condicao()
                self.aceitar("entao")
                if not self.abrir_bloco():
                    self.erro("Depois de 'Senão se ... então' use ':' e continue na linha seguinte")
                senao = [self._se_bloco(tok2, cond2)]
            else:
                if not self.abrir_bloco():
                    self.erro("Depois de 'Senão' use ':' e continue na linha seguinte")
                senao, _ = self.bloco("se", tok_se)
        return Se(tok_se.linha, cond, entao, senao)

    def enquanto(self):
        tok = self.avancar()
        cond = self.condicao()
        self.aceitar("faca")
        if self.abrir_bloco():
            corpo, _ = self.bloco("enquanto", tok)
        else:
            corpo = self.sequencia_simples()
            self.fim_de_instrucao()
        return Enquanto(tok.linha, cond, corpo)

    def repita(self):
        tok = self.avancar()
        vezes = self.quantidade()
        self.esperar_palavra("vezes", descricao="vezes")
        if self.abrir_bloco():
            corpo, _ = self.bloco("repita", tok)
        else:
            corpo = self.sequencia_simples()
            self.fim_de_instrucao()
        return Repita(tok.linha, vezes, corpo)

    def capitulo(self):
        tok = self.avancar()
        nome = self.nome_capitulo()
        if self.atual().tipo != DOIS_PONTOS:
            self.erro("Esperava ':' depois do nome do capítulo")
        if not self.abrir_bloco():
            self.erro("O corpo do capítulo deve começar na linha seguinte ao ':'")
        corpo, _ = self.bloco("capitulo", tok)
        return Capitulo(tok.linha, nome, corpo)

    def nome_capitulo(self):
        if self.atual().tipo == TEXTO:
            palavras = self.avancar().valor.split()
        else:
            palavras = []
            while self.atual().tipo == PALAVRA:
                palavras.append(self.avancar().valor)
        if not palavras:
            self.erro("Esperava o nome do capítulo")
        return Nome(chave_capitulo(palavras), " ".join(palavras))


    def simples(self):
        tok = self.atual()

        if self.eh("mostre"):
            self.avancar()
            self.aceitar(("o", "a", "os", "as"))
            if self.aceitar(("tudo", "todos")):
                return [Mostre(tok.linha, None)]
            return [Mostre(tok.linha, self.sujeito(atualizar=False))]

        if self.eh(("conte", "leia", "releia")):
            self.avancar()
            self.aceitar(("o", "a"))
            self.esperar_palavra("capitulo", descricao="capítulo")
            return [Chamada(tok.linha, self.nome_capitulo())]

        if self.eh("narrador") or tok.tipo == TEXTO:
            if tok.tipo == PALAVRA:
                self.avancar()
                self.aceitar_simbolo(DOIS_PONTOS)
            return [Narracao(tok.linha, self.texto())]

        if self.eh(("o", "a", "os", "as")):
            return [self.atributo_de()]

        if self.eh_pergunta():
            return [self.pergunta()]

        if tok.tipo == PALAVRA and self.eh_operacao_implicita():
            return [self.operacao_implicita()]

        sujeito = self.sujeito()
        verbo = self.atual()

        if self.aceitar(VERBOS_TER):
            if not self.inicio_quantidade():
                self.erro(f"Esperava uma quantidade depois de '{verbo.valor}' (ex.: {sujeito.exibicao} tem 3 maçãs)")
            return self.lista_quantidades(lambda v, item: Declaracao(verbo.linha, sujeito, item, v))
        if self.aceitar(VERBOS_GANHAR):
            return self.lista_quantidades(lambda v, item: Operacao(verbo.linha, sujeito, item, "+", v))
        if self.aceitar(VERBOS_PERDER):
            return self.lista_quantidades(
                lambda v, item: Operacao(verbo.linha, sujeito, item, "-", v), permitir_tudo=True
            )
        if self.eh(("multiplica", "divide")):
            return [self.multiplica_divide(sujeito)]
        if self.eh(("dobra", "triplica")):
            fator = 2 if self.avancar().norm == "dobra" else 3
            return [Operacao(verbo.linha, sujeito, self.item(), "*", fator)]
        if self.aceitar(VERBOS_DAR):
            valor = self.quantidade(permitir_tudo=True)
            item = self.item()
            if not self.aceitar(("para", "pra", "a", "ao")):
                self.erro("Esperava 'para' antes de quem recebe")
            recebedor = self.sujeito(atualizar=False, diferente_de=sujeito)
            return [Transferencia(verbo.linha, sujeito, recebedor, item, valor)]
        if self.aceitar(VERBOS_FALA):
            self.aceitar_simbolo(DOIS_PONTOS)
            return [Fala(verbo.linha, sujeito, verbo.valor.lower(), self.texto())]

        atributo = self.verbo_de_texto()
        if atributo is not None:
            if self.atual().tipo != TEXTO:
                self.erro('Coloque o texto entre aspas (ex.: Maria mora em "Recife")')
            return [DefinirTexto(verbo.linha, sujeito, atributo, self.texto())]

        self.erro(
            f"Não entendi o que '{sujeito.exibicao}' faz: verbos conhecidos são tem, ganha, perde, "
            "dá ... para, multiplica por, divide por, dobra, diz, mora em, é, está, se chama",
            verbo, mostrar_encontrado=False,
        )

    def lista_quantidades(self, construir, permitir_tudo=False):
        nos = []
        while True:
            valor = self.quantidade(permitir_tudo=permitir_tudo)
            nos.append(construir(valor, self.item()))
            separador = self.atual().tipo == VIRGULA or self.eh("e")
            if separador and self.inicio_quantidade(k=1, permitir_tudo=permitir_tudo):
                self.avancar()
                continue
            return nos

    def multiplica_divide(self, sujeito):
        verbo = self.avancar()
        op = "*" if verbo.norm == "multiplica" else "/"
        if self.aceitar("por"):
            valor = self.quantidade()
            item = self.item()
        else:
            item = self.item()
            self.esperar_palavra("por", descricao="por")
            valor = self.quantidade()
        return Operacao(verbo.linha, sujeito, item, op, valor)

    def eh_operacao_implicita(self):
        j = 0
        while self.atual(j).tipo == PALAVRA and self.atual(j).norm not in OPS_IMPLICITAS:
            j += 1
        if j == 0 or not self.eh(set(OPS_IMPLICITAS), k=j):
            return False
        k = j + 1
        if self.atual(j).norm == "dividido":
            if not self.eh("por", k=k):
                return False
            k += 1
        return self.inicio_quantidade(k=k)

    def operacao_implicita(self):
        tok = self.atual()
        palavras = []
        while self.atual().norm not in OPS_IMPLICITAS:
            palavras.append(self.avancar().valor)
        op = OPS_IMPLICITAS[self.avancar().norm]
        self.aceitar("por")
        valor = self.quantidade()
        if self.ultimo_sujeito is None:
            self.erro(f"De quem é '{' '.join(palavras)}'? Cite um personagem antes", tok, mostrar_encontrado=False)
        return Operacao(tok.linha, self.ultimo_sujeito, Nome(*chave_item(palavras)), op, valor)

    def atributo_de(self):
        tok = self.avancar()
        palavras = []
        while self.atual().tipo == PALAVRA and not self.eh("de"):
            palavras.append(self.avancar().valor)
        if not palavras or not self.aceitar("de"):
            self.erro("Esperava 'O <atributo> de <personagem> é \"<texto>\"'", tok)
        sujeito = self.sujeito()
        self.esperar_palavra("e", descricao="é")
        if self.atual().tipo != TEXTO:
            self.erro("Coloque o texto entre aspas")
        return DefinirTexto(tok.linha, sujeito, Nome(*chave_item(palavras)), self.texto())

    def verbo_de_texto(self):
        if self.aceitar("mora", "em"):
            return Nome("cidade", "cidade")
        if self.aceitar("se", "chama") or self.aceitar("chama-se"):
            return Nome("nome", "nome")
        if self.aceitar("trabalha", "como"):
            return Nome("profissao", "profissão")
        if self.aceitar("esta", "em"):
            return Nome("local", "local")
        if self.aceitar(("e", "esta")):
            return Nome("status", "status")
        return None


    def eh_pergunta(self):
        j = 0
        while self.atual(j).tipo not in (PONTO, VIRGULA, NOVA_LINHA, FIM, DOIS_PONTOS, INTERROGACAO):
            j += 1
        return self.atual(j).tipo == INTERROGACAO

    def pergunta(self):
        inicio = self.atual()
        cond = self.condicao()
        fim = self.esperar(INTERROGACAO, "'?' no fim da pergunta")
        return Pergunta(inicio.linha, cond, self.fonte[inicio.inicio : fim.fim])

    def condicao(self):
        esquerda = self.condicao_e()
        while self.eh("ou"):
            tok = self.avancar()
            esquerda = Ou(tok.linha, esquerda, self.condicao_e())
        return esquerda

    def condicao_e(self):
        esquerda = self.condicao_simples()
        while self.eh("e"):
            tok = self.avancar()
            esquerda = E(tok.linha, esquerda, self.condicao_simples())
        return esquerda

    def condicao_simples(self):
        tok = self.atual()
        sujeito = self.sujeito()
        negar = self.aceitar("nao")
        if self.aceitar(("tiver", "tem", "possui", "possuir")):
            if negar and self.eh(("nenhum", "nenhuma")):
                negar = False
            cond = self.condicao_quantidade(tok.linha, sujeito)
        else:
            atributo = self.verbo_de_texto()
            if atributo is None:
                self.erro(f"Esperava 'tiver' depois de '{sujeito.exibicao}' na condição")
            texto = self.esperar(TEXTO, "um texto entre aspas")
            cond = TextoIgual(tok.linha, sujeito, atributo, texto.valor)
        return Nao(tok.linha, cond) if negar else cond

    def condicao_quantidade(self, linha, sujeito):
        for palavras, op in (
            (("mais", "de"), ">"), (("menos", "de"), "<"), (("pelo", "menos"), ">="),
            (("no", "maximo"), "<="), (("exatamente",), "=="),
        ):
            if self.aceitar(*palavras):
                valor = self.quantidade()
                return Comparacao(linha, sujeito, self.item(), op, valor)
        if self.aceitar(("nenhum", "nenhuma")):
            return Comparacao(linha, sujeito, self.item(), "==", 0)
        if self.eh(("mais", "menos")):
            op = ">" if self.avancar().norm == "mais" else "<"
            item = self.item()
            if not (self.aceitar("do", "que") or self.aceitar("que")):
                self.erro("Esperava 'do que' na comparação")
            return self.comparar_com(linha, sujeito, item, op)
        if self.aceitar(("tantos", "tantas")):
            item = self.item()
            self.esperar_palavra("quanto", descricao="quanto")
            return self.comparar_com(linha, sujeito, item, "==")
        if self.inicio_quantidade():
            valor = self.quantidade()
            return Comparacao(linha, sujeito, self.item(), ">=", valor)
        return Comparacao(linha, sujeito, self.item(), ">", 0)

    def comparar_com(self, linha, sujeito, item, op):
        if self.inicio_quantidade():
            return Comparacao(linha, sujeito, item, op, self.quantidade())
        return ComparacaoEntre(linha, sujeito, self.sujeito(atualizar=False), item, op)


    def sujeito(self, atualizar=True, diferente_de=None):
        tok = self.atual()
        if tok.tipo != PALAVRA:
            self.erro("Esperava o nome de um personagem")
        if tok.norm in PRONOMES:
            candidatos = [s for s in self.recentes if s != diferente_de]
            if not candidatos:
                self.erro(f"Não sei a quem '{tok.valor}' se refere: cite o personagem antes", mostrar_encontrado=False)
            self.avancar()
            return candidatos[0]
        if tok.norm in RESERVADAS:
            self.erro(f"'{tok.valor}' é uma palavra reservada e não pode ser nome de personagem", mostrar_encontrado=False)
        self.avancar()
        nome = Nome(chave_personagem(tok.valor), tok.valor)
        self.citar(nome, como_sujeito=atualizar)
        return nome

    def citar(self, nome, como_sujeito):
        if nome in self.recentes:
            self.recentes.remove(nome)
        if como_sujeito or not self.recentes:
            self.recentes.insert(0, nome)
        else:
            self.recentes.insert(1, nome)

    @property
    def ultimo_sujeito(self):
        return self.recentes[0] if self.recentes else None

    def quantidade(self, permitir_tudo=False):
        tok = self.atual()
        if tok.tipo == NUMERO:
            return self.avancar().valor
        if tok.tipo == PALAVRA and tok.norm in EXTENSO:
            return EXTENSO[self.avancar().norm]
        if permitir_tudo and self.aceitar(TODOS):
            self.aceitar(("as", "os"))
            return None
        self.erro("Esperava uma quantidade (ex.: 3 ou três)")

    def item(self):
        while self.eh(POSSESSIVOS) and self.atual(1).tipo == PALAVRA:
            self.avancar()
        palavras = []
        while self.atual().tipo == PALAVRA and self.atual().norm not in PARADAS_ITEM:
            palavras.append(self.avancar().valor)
        if not palavras:
            self.erro("Esperava o nome de um item (ex.: maçãs)")
        return Nome(*chave_item(palavras))

    def texto(self):
        tok = self.esperar(TEXTO, "um texto entre aspas")
        bruto, partes, pos = tok.valor, [], 0
        while pos < len(bruto):
            abre = bruto.find("{", pos)
            if abre < 0:
                partes.append(bruto[pos:])
                break
            if bruto.startswith("{{", abre):
                partes.append(bruto[pos:abre] + "{")
                pos = abre + 2
                continue
            fecha = bruto.find("}", abre)
            if fecha < 0:
                self.erro("Texto com '{' sem '}' correspondente", tok, mostrar_encontrado=False)
            partes.append(bruto[pos:abre])
            referencia = bruto[abre + 1 : fecha].strip()
            if "." not in referencia:
                self.erro(
                    f"Referência '{{{referencia}}}' inválida: use {{personagem.item}}",
                    tok, mostrar_encontrado=False,
                )
            quem, oque = (p.strip() for p in referencia.split(".", 1))
            partes.append(Referencia(
                tok.linha,
                Nome(chave_personagem(quem), quem),
                Nome(*chave_item(separar_palavras_item(oque))),
            ))
            pos = fecha + 1
        return Texto(tok.linha, [p for p in partes if p != ""])


def analisar_sintaxe(tokens, fonte, ultimo_sujeito=None):
    return Parser(tokens, fonte, ultimo_sujeito).programa()
