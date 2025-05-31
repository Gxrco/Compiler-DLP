# YAPar/codegen/generator.py

import argparse
import sys
import os
from YAPar.grammar_parser      import parse_file
from YAPar.lr0_builder         import build_lr0_states
from YAPar.slr_table_generator import build_slr_parsing_table

def generate_parser(grammar_path: str, output_path: str):
    """
    Genera un archivo Python con:
      - PRODUCTIONS: lista de producciones [(lhs, [rhs1, rhs2, ...]), ...]
      - ACTION: tabla SLR(1) de shift/reduce/accept
      - GOTO: tabla SLR(1) de transiciones sobre no-terminales
      - parse(tokens): función autónoma que devuelve la secuencia de acciones
      - En modo standalone, recibe tokens por stdin y muestra el log
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

            # Incrustar PRODUCTIONS, ACTION, GOTO
            out.write("PRODUCTIONS = ")
            out.write(repr(prods))
            out.write("\n\n")

            out.write("ACTION = ")
            out.write(repr(action_tbl))
            out.write("\n\n")

            out.write("GOTO = ")
            out.write(repr(goto_tbl))
            out.write("\n\n")

            # Función parse autónoma
            out.write("def parse(tokens):\n")
            out.write("    \"\"\"Parser SLR(1) autónomo: recibe lista de token names y devuelve acciones.\"\"\"\n")
            out.write("    state_stack = [0]\n")
            out.write("    symbol_stack = []\n")
            out.write("    log = []\n")
            out.write("    tokens = tokens + ['$']  # agregamos EOF al final\n")
            out.write("    for a in tokens:\n")
            out.write("        while True:\n")
            out.write("            s = state_stack[-1]\n")
            out.write("            act = ACTION.get((s, a))\n")
            out.write("            if act is None:\n")
            out.write("                raise Exception(f\"Token inesperado '{a}' en estado {s}\")\n")
            out.write("            kind, target = act\n")
            out.write("            if kind == 'shift':\n")
            out.write("                log.append((s, f\"shift {a}\"))\n")
            out.write("                symbol_stack.append(a)\n")
            out.write("                state_stack.append(target)\n")
            out.write("                break  # avanzamos al siguiente token\n")
            out.write("            elif kind == 'reduce':\n")
            out.write("                lhs, rhs_list = PRODUCTIONS[target]\n")
            out.write("                # Elegir la alternativa que coincide con el final de la pila\n")
            out.write("                chosen_rhs = None\n")
            out.write("                for alt in rhs_list:\n")
            out.write("                    if len(alt) <= len(symbol_stack) and symbol_stack[-len(alt):] == alt:\n")
            out.write("                        chosen_rhs = alt\n")
            out.write("                        break\n")
            out.write("                if chosen_rhs is None:\n")
            out.write("                    chosen_rhs = rhs_list[0]\n")
            out.write("                # Desapilar |chosen_rhs| símbolos y estados\n")
            out.write("                for _ in chosen_rhs:\n")
            out.write("                    symbol_stack.pop()\n")
            out.write("                    state_stack.pop()\n")
            out.write("                log.append((s, f\"reduce {lhs} -> {' '.join(chosen_rhs)}\"))\n")
            out.write("                s2 = state_stack[-1]\n")
            out.write("                j = GOTO.get((s2, lhs))\n")
            out.write("                if j is None:\n")
            out.write("                    raise Exception(f\"No hay GOTO para '{lhs}' en estado {s2}\")\n")
            out.write("                symbol_stack.append(lhs)\n")
            out.write("                state_stack.append(j)\n")
            out.write("                # Seguimos evaluando el mismo token 'a'\n")
            out.write("                continue\n")
            out.write("            elif kind == 'accept':\n")
            out.write("                log.append((s, 'accept'))\n")
            out.write("                return log\n")
            out.write("            else:\n")
            out.write("                raise Exception(f\"Acción desconocida '{kind}' en estado {s}\")\n")
            out.write("    return log\n\n")

            # Modo standalone: leer tokens por stdin y mostrar log
            out.write("if __name__ == '__main__':\n")
            out.write("    import sys\n")
            out.write("    data = sys.stdin.read().split()\n")
            out.write("    try:\n")
            out.write("        result = parse(data)\n")
            out.write("        for state, action in result:\n")
            out.write("            print(state, action)\n")
            out.write("    except Exception as e:\n")
            out.write("        print('Error durante el parseo:', e)\n")

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
