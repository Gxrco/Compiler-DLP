# YAPar/cli.py

import argparse
import sys
from YAPar.grammar_parser      import parse_file
from YAPar.utils.first_follow  import compute_first, compute_follow
from YAPar.lr0_builder         import build_lr0_states
from YAPar.slr_table_generator import build_slr_parsing_table
from YAPar.errors              import CLIError, GrammarError, GenerationError
from YAPar.utils.visualize_lr0 import lr0_to_dot

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
    parser.add_argument("--visualize", action="store_true",
                        help="Generar visualización del autómata LR(0) como PDF")

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

    # 4.5) Visualizar LR(0) si se pidió
    if args.visualize:
        try:
            lr0_to_dot(args.grammar, output_dot="lr0_states")
            print("Visualización LR(0) generada: lr0_states.pdf")
        except Exception as e:
            print(f"Error al generar visualización LR(0): {e}", file=sys.stderr)

    # 5) Prueba de parsing si se indicó --test
    if args.test_input:
        try:
            with open(args.test_input, encoding="utf-8") as f:
                tokens = f.read().split()
            print(f"Probando parseo con tokens de {args.test_input}: {tokens}")
            # Ejecutamos nuestro parser autónomo una vez generado
            # Pero aun no lo hemos generado; podemos posponer esto hasta después de escribir el archivo
        except FileNotFoundError:
            print(f"No se encontró archivo de prueba: {args.test_input}", file=sys.stderr)
            sys.exit(1)

    # 6) Generar archivo parser Python autónomo
    try:
        with open(args.output, "w", encoding="utf-8") as out:
            out.write("#!/usr/bin/env python3\n")
            out.write("# Parser generado por YAPar CLI\n\n")
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
            out.write("                chosen_rhs = None\n")
            out.write("                for alt in rhs_list:\n")
            out.write("                    if len(alt) <= len(symbol_stack) and symbol_stack[-len(alt):] == alt:\n")
            out.write("                        chosen_rhs = alt\n")
            out.write("                        break\n")
            out.write("                if chosen_rhs is None:\n")
            out.write("                    chosen_rhs = rhs_list[0]\n")
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
            out.write("                continue\n")
            out.write("            elif kind == 'accept':\n")
            out.write("                log.append((s, 'accept'))\n")
            out.write("                return log\n")
            out.write("            else:\n")
            out.write("                raise Exception(f\"Acción desconocida '{kind}' en estado {s}\")\n")
            out.write("    return log\n\n")

            out.write("if __name__ == '__main__':\n")
            out.write("    import sys\n")
            out.write("    data = sys.stdin.read().split()\n")
            out.write("    try:\n")
            out.write("        result = parse(data)\n")
            out.write("        for state, action in result:\n")
            out.write("            print(state, action)\n")
            out.write("    except Exception as e:\n")
            out.write("        print('Error durante el parseo:', e)\n")

        print(f"Parser generado en {args.output}")
    except OSError as e:
        print(f"Error al escribir el parser: {e}", file=sys.stderr)
        sys.exit(1)

    # 7) Si se pidió --test, ejecutar inmediatamente el test de parseo
    if args.test_input:
        try:
            with open(args.test_input, encoding="utf-8") as f:
                tokens = f.read().split()
        except FileNotFoundError:
            print(f"No se encontró archivo de prueba: {args.test_input}", file=sys.stderr)
            sys.exit(1)

        # Importar el parser recién generado y ejecutar parse(tokens)
        import importlib.util
        spec = importlib.util.spec_from_file_location("theparser_test", args.output)
        test_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_mod)

        print(f"\nProbando parseo con tokens de {args.test_input}: {tokens}")
        try:
            acciones = test_mod.parse(tokens)
            for s, a in acciones:
                print(s, a)
            if acciones and acciones[-1][1] == "accept":
                print("\n--- ¡¡Parseo de prueba exitoso (accept)!! ---")
            else:
                print("\n--- El parseo de prueba NO llegó a 'accept'.---")
        except Exception as e:
            print("Error durante el parseo de prueba:", e)

if __name__ == "__main__":
    try:
        main()
    except CLIError as e:
        print(f"CLI error: {e}", file=sys.stderr)
        sys.exit(1)
