# YALex/app.py

import argparse
import sys
import os

# ──────────────────────────────────────────────────────────────────────────────
# Para que Python encuentre chain_compiler y afd_compiler que están dentro de YALex:
# Añadimos la carpeta 'YALex' a sys.path
this_dir = os.path.dirname(os.path.abspath(__file__))
if this_dir not in sys.path:
    sys.path.insert(0, this_dir)
# ──────────────────────────────────────────────────────────────────────────────

from chain_compiler.tools.yal_parser import parse_yal_file
from lex_compiler.service         import generate_lexer_py

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generador de lexer a partir de .yal y escáner opcional'
    )
    parser.add_argument(
        '--yal', '-y',
        required=True,
        help='Ruta a un archivo .yal'
    )
    parser.add_argument(
        '--out', '-o',
        default='thelexer.py',
        help='Ruta de salida para el lexer generado'
    )
    parser.add_argument(
        '--scan_file', '-s',
        help='(Opcional) Ruta a un archivo para escaneo con el lexer generado'
    )
    args = parser.parse_args()

    # 1) Parsear .yal
    yal_info = parse_yal_file(args.yal)
    if yal_info is None:
        print(f"Error: no se pudo parsear {args.yal}")
        sys.exit(1)

    # 2) Generar thelexer.py
    generate_lexer_py(yal_info, args.out)
    print(f"Lexer generado en {args.out}")

    # 3) Si pidieron escaneo, cargar y usar entrypoint
    if args.scan_file:
        spec = None
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "thelexer", os.path.abspath(args.out)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"Error al cargar el lexer generado: {e}")
            sys.exit(1)

        data = ""
        try:
            with open(args.scan_file, encoding='utf-8') as f:
                data = f.read()
        except FileNotFoundError:
            print(f"Error: no se encontró el archivo {args.scan_file}")
            sys.exit(1)

        for tok, lex in mod.entrypoint(data):
            print(tok, lex)
