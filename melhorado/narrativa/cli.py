import argparse
import sys
from pathlib import Path

from . import __version__
from .erros import ErroNarrativo
from .gerador import gerar_python
from .interpretador import Interpretador
from .lexer import tokenizar
from .nos import formatar_ast
from .parser import Parser, analisar_sintaxe
from .runtime import LIMITE_LACO_PADRAO
from .semantica import analisar_semantica, exigir_sem_erros


def _ler(caminho):
    try:
        return Path(caminho).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho}' não foi encontrado.", file=sys.stderr)
        sys.exit(2)


def _analisar(fonte, mostrar_avisos=True):
    programa = analisar_sintaxe(tokenizar(fonte), fonte)
    diagnosticos = analisar_semantica(programa)
    if mostrar_avisos:
        for d in diagnosticos:
            print(d, file=sys.stderr)
    exigir_sem_erros(diagnosticos)
    return programa, diagnosticos


def cmd_executar(args, fonte):
    programa, _ = _analisar(fonte, mostrar_avisos=not args.silencioso)
    Interpretador(print, args.limite_laco, args.trace).executar(programa)


def cmd_compilar(args, fonte):
    programa, _ = _analisar(fonte)
    codigo = gerar_python(programa, Path(args.arquivo).name, args.limite_laco)
    destino = Path(args.saida) if args.saida else Path(args.arquivo).with_suffix(".py")
    destino.write_text(codigo, encoding="utf-8")
    print(f"✅ Compilado: {destino}  (rode com: python {destino})")


def cmd_verificar(args, fonte):
    _, diagnosticos = _analisar(fonte)
    avisos = sum(d.nivel == "aviso" for d in diagnosticos)
    print(f"✅ Nenhum erro encontrado ({avisos} aviso(s)).")


def cmd_tokens(args, fonte):
    for tok in tokenizar(fonte):
        valor = "" if tok.valor in (None, "\n") else repr(tok.valor)
        print(f"{tok.linha:>4}:{tok.coluna:<4} {tok.tipo:<13} {valor}")


def cmd_ast(args, fonte):
    print(formatar_ast(analisar_sintaxe(tokenizar(fonte), fonte)))


def cmd_repl(args):
    print(f"Linguagem Narrativa {__version__} - modo interativo. Escreva 'sair' para terminar.")
    interp = Interpretador(print, args.limite_laco)
    ultimo_sujeito = None
    pendente, profundidade = [], 0
    while True:
        try:
            linha = input("... " if pendente else ">>> ")
        except EOFError:
            print()
            return
        if not pendente and linha.strip().lower() in ("sair", "exit", "quit"):
            return
        pendente.append(linha)
        frase = linha.split("#", 1)[0].strip().lower()
        if frase.endswith(":") and not frase.startswith(("senão", "senao")):
            profundidade += 1
        elif frase.startswith("fim"):
            profundidade -= 1
        if profundidade > 0:
            continue
        fonte, pendente, profundidade = "\n".join(pendente), [], 0
        try:
            parser = Parser(tokenizar(fonte), fonte, ultimo_sujeito)
            programa = parser.programa()
            ultimo_sujeito = parser.ultimo_sujeito
            interp.executar(programa)
        except ErroNarrativo as erro:
            print(erro.formatar(fonte), file=sys.stderr)


def criar_parser():
    parser = argparse.ArgumentParser(
        prog="narrativa",
        description="Linguagem Narrativa: programe contando uma história.",
    )
    parser.add_argument("--versao", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="comando")

    def com_arquivo(nome, ajuda):
        p = sub.add_parser(nome, help=ajuda)
        p.add_argument("arquivo", help="arquivo da história (.hist ou .txt)")
        p.add_argument("--limite-laco", type=int, default=LIMITE_LACO_PADRAO,
                       help=f"máximo de voltas de um 'Enquanto' (padrão {LIMITE_LACO_PADRAO})")
        return p

    p = com_arquivo("executar", "executa a história")
    p.add_argument("--trace", action="store_true", help="mostra a memória após cada instrução")
    p.add_argument("--silencioso", action="store_true", help="não mostra avisos")
    p = com_arquivo("compilar", "gera um programa Python equivalente")
    p.add_argument("-o", "--saida", help="arquivo .py de saída (padrão: mesmo nome da história)")
    com_arquivo("verificar", "só verifica erros (léxico, sintaxe e semântica)")
    com_arquivo("tokens", "mostra os tokens (saída do analisador léxico)")
    com_arquivo("ast", "mostra a árvore sintática (saída do parser)")
    p = sub.add_parser("repl", help="modo interativo")
    p.add_argument("--limite-laco", type=int, default=LIMITE_LACO_PADRAO)
    return parser


COMANDOS = {
    "executar": cmd_executar, "compilar": cmd_compilar, "verificar": cmd_verificar,
    "tokens": cmd_tokens, "ast": cmd_ast,
}


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    parser = criar_parser()
    args = parser.parse_args(argv)
    if args.comando is None:
        parser.print_help()
        return 0
    if args.comando == "repl":
        cmd_repl(args)
        return 0
    fonte = _ler(args.arquivo)
    try:
        COMANDOS[args.comando](args, fonte)
    except ErroNarrativo as erro:
        print(erro.formatar(fonte), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
