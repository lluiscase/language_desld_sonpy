LIMITE_LACO_PADRAO = 10_000
LIMITE_CAPITULOS = 200

_COMPARADORES = {
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
}


def plural(palavra, quantidade):
    if quantidade == 1:
        return palavra
    def uma(p):
        if p.endswith("ão"):
            return p[:-2] + "ões"
        if p.endswith("m"):
            return p[:-1] + "ns"
        if p.endswith(("r", "z")):
            return p + "es"
        if p.endswith("s"):
            return p
        return p + "s"
    return " ".join(uma(p) for p in palavra.split())


class Memoria:
    def __init__(self, erro, limite_laco=LIMITE_LACO_PADRAO):
        self.erro = erro
        self.limite_laco = limite_laco
        self.dados = {}
        self.nomes = {}
        self.itens = {}
        self.pilha = []


    def _falhar(self, mensagem, linha):
        raise self.erro(mensagem, linha)

    def _nome(self, sujeito):
        return self.nomes.get(sujeito[0], sujeito[1])

    def _variaveis(self, sujeito, item):
        self.nomes.setdefault(sujeito[0], sujeito[1])
        self.itens.setdefault(item[0], item[1])
        return self.dados.setdefault(sujeito[0], {})

    def _ler(self, sujeito, item):
        return self.dados.get(sujeito[0], {}).get(item[0])

    def numero(self, sujeito, item, linha, obrigatorio=True):
        valor = self._ler(sujeito, item)
        if valor is None:
            if obrigatorio:
                self._falhar(f"{self._nome(sujeito)} ainda não tem nenhum(a) {item[1]}", linha)
            return 0
        if isinstance(valor, str):
            self._falhar(f"'{item[1]}' de {self._nome(sujeito)} é um texto, não uma quantidade", linha)
        return valor

    def _guardar_numero(self, sujeito, item, valor, linha):
        variaveis = self._variaveis(sujeito, item)
        if isinstance(variaveis.get(item[0]), str):
            self._falhar(f"'{item[1]}' de {self._nome(sujeito)} é um texto, não uma quantidade", linha)
        variaveis[item[0]] = valor


    def declarar(self, sujeito, item, valor, linha):
        self._guardar_numero(sujeito, item, valor, linha)

    def definir_texto(self, sujeito, atributo, texto, linha):
        variaveis = self._variaveis(sujeito, atributo)
        if isinstance(variaveis.get(atributo[0]), int):
            self._falhar(f"'{atributo[1]}' de {self._nome(sujeito)} é uma quantidade, não um texto", linha)
        variaveis[atributo[0]] = texto

    def operar(self, sujeito, item, op, valor, linha):
        atual = self.numero(sujeito, item, linha, obrigatorio=(op != "+"))
        if op == "+":
            novo = atual + valor
        elif op == "-":
            if valor is None:
                valor = atual
            if valor > atual:
                self._falhar(
                    f"{self._nome(sujeito)} tem só {atual} {plural(item[1], atual)} "
                    f"e não pode perder {valor}", linha)
            novo = atual - valor
        elif op == "*":
            novo = atual * valor
        elif op == "/":
            if valor == 0:
                self._falhar("Divisão por zero", linha)
            novo = atual // valor
        else:
            self._falhar(f"Operação desconhecida {op!r}", linha)
        self._guardar_numero(sujeito, item, novo, linha)

    def transferir(self, doador, recebedor, item, valor, linha):
        saldo = self.numero(doador, item, linha, obrigatorio=False)
        if valor is None:
            valor = saldo
        if valor > saldo:
            self._falhar(
                f"{self._nome(doador)} não tem {valor} {plural(item[1], valor)} para dar "
                f"(tem {saldo})", linha)
        self._guardar_numero(doador, item, saldo - valor, linha)
        destino = self.numero(recebedor, item, linha, obrigatorio=False)
        self._guardar_numero(recebedor, item, destino + valor, linha)


    def comparar(self, sujeito, item, op, valor, linha):
        return _COMPARADORES[op](self.numero(sujeito, item, linha, obrigatorio=False), valor)

    def comparar_entre(self, sujeito, outro, item, op, linha):
        a = self.numero(sujeito, item, linha, obrigatorio=False)
        b = self.numero(outro, item, linha, obrigatorio=False)
        return _COMPARADORES[op](a, b)

    def texto_igual(self, sujeito, atributo, texto, linha):
        valor = self._ler(sujeito, atributo)
        return isinstance(valor, str) and valor.casefold() == texto.casefold()


    def interpolar(self, partes, linha):
        resultado = []
        for parte in partes:
            if isinstance(parte, str):
                resultado.append(parte)
                continue
            sujeito, item = parte
            valor = self._ler(sujeito, item)
            if valor is None:
                self._falhar(
                    f"O texto usa {{{sujeito[1]}.{item[1]}}}, mas {self._nome(sujeito)} "
                    f"não tem '{item[1]}'", linha)
            resultado.append(str(valor))
        return "".join(resultado)

    def fala(self, sujeito, verbo, partes, linha):
        return f'🗣️  {self._nome(sujeito)} {verbo}: "{self.interpolar(partes, linha)}"'

    def narrar(self, partes, linha):
        return f"📖 {self.interpolar(partes, linha)}"

    def perguntar(self, texto, resposta):
        return f"❓ {texto} {'Sim' if resposta else 'Não'}"

    def _descrever(self, chave):
        variaveis = self.dados.get(chave, {})
        if not variaveis:
            return f"📦 {self.nomes.get(chave, chave)} → (nada)"
        itens = " | ".join(
            f"{self.itens[k]}: " + (f'"{v}"' if isinstance(v, str) else str(v))
            for k, v in variaveis.items()
        )
        return f"📦 {self.nomes[chave]} → {itens}"

    def mostrar(self, sujeito=None):
        if sujeito is not None:
            self.nomes.setdefault(sujeito[0], sujeito[1])
            return self._descrever(sujeito[0])
        if not self.dados:
            return "📦 (ninguém na história ainda)"
        return "\n".join(self._descrever(chave) for chave in self.dados)


    def passo_laco(self, contador, linha):
        if contador > self.limite_laco:
            self._falhar(
                f"O laço repetiu mais de {self.limite_laco} vezes (possível laço infinito)", linha)

    def entrar(self, capitulo, linha):
        if len(self.pilha) >= LIMITE_CAPITULOS:
            self._falhar(
                f"Capítulos chamando uns aos outros mais de {LIMITE_CAPITULOS} vezes "
                f"(o capítulo '{capitulo}' nunca termina?)", linha)
        self.pilha.append(capitulo)

    def sair(self):
        self.pilha.pop()

    def memoria_plana(self):
        return {f"{s}.{i}": v for s, variaveis in self.dados.items() for i, v in variaveis.items()}
