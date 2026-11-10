import argparse
import sys
from historia.core import InterpretadorNarrativo

def main():
    parser = argparse.ArgumentParser(
        description="Interpretador de Linguagem Narrativa baseada em Histórias."
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    exec_parser = subparsers.add_parser("executar", help="Executa um arquivo .txt de história")
    exec_parser.add_argument("arquivo", type=str, help="Caminho do arquivo .txt")

    args = parser.parse_args()

    if args.comando == "executar":
        interpretador = InterpretadorNarrativo()
        try:
            resultados = interpretador.interpretar_arquivo(args.arquivo)
            print("\n--- INÍCIO DA EXECUÇÃO ---")
            for res in resultados:
                if res:
                    print(res)
            print("--- FIM DA EXECUÇÃO ---\n")
        except FileNotFoundError:
            print(f"Erro: Arquivo '{args.arquivo}' não encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
