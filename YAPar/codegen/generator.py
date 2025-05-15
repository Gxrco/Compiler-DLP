# YAPar/codegen/generator.py

import argparse
import sys
from YAPar.grammar_parser      import parse_file
from YAPar.lr0_builder         import build_lr0_states
from YAPar.slr_table_generator import build_slr_parsing_table

def generate_parser(grammar_path: str, output_path: str):
    """
    Genera un archivo Python con:
      - PRODUCTIONS: lista de producciones [(lhs, [rhs1, rhs2, ...]), ...]
      - ACTION: tabla SLR(1) de shift/reduce/accept
      - GOTO: tabla SLR(1) de transiciones sobre no-terminales
      - parse(tokens): función que delega en parse_engine.parse_tokens
    """
    # 1) Leer gramática y preparativos
    grammar = parse_file(grammar_path)
    prods   = [(p.lhs, p.rhs) for p in grammar.productions]

    # 2) Generar tablas SLR(1)
    states, action_tbl, goto_tbl = build_slr_parsing_table(grammar_path)

    # 3) Escribir el archivo de salida
    try:
        with open(output_path, "w", encoding="utf-8") as out:
            out.write("#!/usr/bin/env python3\n")
            out.write("# Parser generado por YAPar\n\n")

            out.write("PRODUCTIONS = ")
            out.write(repr(prods))
            out.write("\n\n")

            out.write("ACTION = ")
            out.write(repr(action_tbl))
            out.write("\n\n")

            out.write("GOTO = ")
            out.write(repr(goto_tbl))
            out.write("\n\n")

            out.write("def parse(tokens):\n")
            out.write("    \"\"\"Parser SLR(1) embebido: recibe lista de tokens y devuelve acciones.\"\"\"\n")
            out.write("    from YAPar.parse_engine import parse_tokens\n")
            out.write("    # Usa el archivo actual (__file__) como gramática\n")
            out.write("    return parse_tokens(__file__, tokens)\n\n")

            out.write("if __name__ == '__main__':\n")
            out.write("    import sys\n")
            out.write("    data = sys.stdin.read().split()\n")
            out.write("    result = parse(data)\n")
            out.write("    for state, action in result:\n")
            out.write("        print(state, action)\n")
        print(f"Parser generado en {output_path}")
    except IOError as e:
        print(f"Error al escribir el parser: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="yapar-codegen",
        description="Genera un parser Python SLR(1) a partir de una gramática .yalp"
    )
    parser.add_argument(
        "grammar",
        help="Ruta al archivo de gramática (.yalp)"
    )
    parser.add_argument(
        "-o", "--output",
        dest="output",
        required=True,
        help="Nombre del archivo Python de salida"
    )
    args = parser.parse_args()

    generate_parser(args.grammar, args.output)


if __name__ == "__main__":
    main()
