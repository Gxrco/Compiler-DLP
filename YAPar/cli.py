# YAPar/cli.py

import argparse
import sys
from YAPar.grammar_parser      import parse_file
from YAPar.utils.first_follow  import compute_first, compute_follow
from YAPar.lr0_builder         import build_lr0_states
from YAPar.slr_table_generator import build_slr_parsing_table
from YAPar.parse_engine        import parse_tokens, ParseError
from YAPar.errors              import CLIError, GrammarError, GenerationError

def main():
    parser = argparse.ArgumentParser(
        prog="yapar",
        description="YAPar CLI: genera y prueba un parser SLR(1) desde una gramática .yalp"
    )
    parser.add_argument("grammar", help="Ruta al archivo de gramática (.yalp)")
    parser.add_argument("-l", "--lexer", dest="lexer",
                        help="Archivo de lexer generado por YALex (no usado actualmente)")
    parser.add_argument("-o", "--output", dest="output", required=True,
                        help="Nombre del archivo Python de salida para el parser")
    parser.add_argument("--test", dest="test_input",
                        help="Archivo con tokens de prueba (tokens separados por espacio)")

    # Permitir --help sin convertirlo en CLIError
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            raise CLIError("Error en los argumentos de la línea de comandos")
        else:
            sys.exit(0)

    # 1) Parsear gramática
    try:
        grammar = parse_file(args.grammar)
    except GrammarError as e:
        print(f"Error de gramática: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Cargando gramática desde {args.grammar}")
    print(f"Tokens declarados: {grammar.tokens}")
    print(f"No-terminales: {[p.lhs for p in grammar.productions]}")

    # 2) FIRST / FOLLOW
    first  = compute_first(grammar)
    follow = compute_follow(grammar, first)
    print("FIRST sets calculados")
    print("FOLLOW sets calculados")

    # 3) LR(0) Collection
    prods = [(p.lhs, p.rhs) for p in grammar.productions]
    start_prime = grammar.start_symbol + "'"
    aug_prods   = [(start_prime, [[grammar.start_symbol]])] + prods
    states = build_lr0_states(aug_prods, start_prime)
    print(f"{len(states)} estados LR(0) generados")

    # 4) Tablas SLR(1)
    try:
        _, action_tbl, goto_tbl = build_slr_parsing_table(args.grammar)
    except Exception as e:
        print(f"Error al generar tablas SLR(1): {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Tabla ACTION con {len(action_tbl)} entradas")
    print(f"Tabla GOTO con {len(goto_tbl)} entradas")

    # 5) Prueba de parsing si se indicó --test
    if args.test_input:
        try:
            with open(args.test_input, encoding='utf-8') as f:
                tokens = f.read().split()
            print(f"Probando parseo con tokens de {args.test_input}: {tokens}")
            actions = parse_tokens(args.grammar, tokens)
            for state, act in actions:
                print(f"{state}: {act}")
        except ParseError as e:
            print(f"Parse error: {e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"No se encontró archivo de prueba: {args.test_input}", file=sys.stderr)
            sys.exit(1)

    # 6) Generar archivo parser Python
    try:
        with open(args.output, "w", encoding='utf-8') as out:
            out.write("#!/usr/bin/env python3\n")
            out.write("# Parser generado por YAPar CLI\n\n")
            out.write("ACTION = ")
            out.write(repr(action_tbl))
            out.write("\n\n")
            out.write("GOTO = ")
            out.write(repr(goto_tbl))
            out.write("\n\n")
            out.write("def parse(tokens):\n")
            out.write("    \"\"\"Parser SLR(1) embebido: recibe lista de tokens y devuelve acciones.\"\"\"\n")
            out.write("    from YAPar.parse_engine import parse_tokens\n")
            out.write("    return parse_tokens(__file__, tokens)\n\n")
            out.write("if __name__ == '__main__':\n")
            out.write("    import sys\n")
            out.write("    data = sys.stdin.read().split()\n")
            out.write("    result = parse(data)\n")
            out.write("    for s, a in result:\n")
            out.write("        print(s, a)\n")
        print(f"Parser generado en {args.output}")
    except OSError as e:
        print(f"Error al escribir el parser: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except CLIError as e:
        print(f"CLI error: {e}", file=sys.stderr)
        sys.exit(1)
