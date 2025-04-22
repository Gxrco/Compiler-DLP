from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService
from file_processor import read_regex_from_file
import argparse
from chain_compiler.tools.yal_parser import parse_yal_file
import re
from chain_compiler.tools.super_regex_builder import build_super_regex
from lex_compiler.service import generate_lexer_py
import sys


def scan_input_file(filepath, afd_service):
    """
    Lee un archivo de entrada y utiliza el método scan_input del AFD para extraer tokens.
    Construye y muestra la tabla de símbolos (tokens válidos).
    
    Args:
        filepath (str): Ruta al archivo de entrada.
        afd_service (AFDService): Instancia del servicio AFD ya construido.
    """
    symbol_table = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.rstrip('\n')
            tokens = afd_service.scan_input(line)
            print(f"Línea {line_number}: {tokens}")
            for token_type, lexeme in tokens:
                # Agregar a la tabla solo tokens válidos; se ignoran los errores o tokens a omitir.
                if token_type not in ["ERROR", "SPACE"]:
                    symbol_table.append({
                        "line": line_number,
                        "token": token_type,
                        "lexeme": lexeme
                    })
    print("\nTabla de símbolos:")
    for entry in symbol_table:
        print(entry)

def process_regex(regex, test_strings=None):
    """
    Procesa una expresión regular, construye el AST, el DFA y lo prueba con cadenas de prueba.
    
    Args:
        regex (str): La expresión regular a procesar
        test_strings (list): Lista opcional de cadenas para probar
    """
    print("Expresión regular:", regex)
    
    # Tokenizar la regex
    tokens = normalize_regex(regex)
    print("Tokens normalizados:", tokens)
    
    # Convertir a notación postfix
    postfix = parse_tokens(tokens)
    print("Notación postfix:", postfix)
    
    # Generar el AST
    ast = generate_ast(postfix)
    print("AST:")
    print(ast.pretty_print())
    
    # Construir y visualizar el AST
    ast_graph = build_ast_graph(ast)
    ast_graph.render('ast_graph', view=False)
    
    # Construir el DFA a partir del AST
    afd_service = AFDService()
    dfa = afd_service.build_dfa_from_ast(ast)
    
    # Generar un nombre de archivo único para el DFA normal
    safe_regex = regex.replace("?", "optional").replace("*", "star").replace("+", "plus").replace("|", "or")
    safe_regex = re.sub(r'[^\w\-_]', '', safe_regex)
    normal_filename = f'dfa_normal_{safe_regex[:30]}'
    dfa.visualize(normal_filename)
    
    # Minimizar el DFA
    minimized_dfa = afd_service.minimize_dfa()
    
    # Generar un nombre de archivo único para el DFA minimizado
    minimized_filename = f'dfa_minimized_{safe_regex[:30]}'
    minimized_dfa.visualize(minimized_filename)
    
    # Probar cadenas con el DFA minimizado
    if test_strings is None:
        test_strings = ["bcdfghjklmnpqrstvwxyz"]  # Cadenas de prueba predeterminadas
    
    print("\nProbando cadenas con el AFD minimizado:")
    for s in test_strings:
        result = afd_service.match(s)
        status = 'Aceptada' if result else 'Rechazada'
        token = f" (Token: {result})" if result else ""
        print(f"'{s}': {status}{token}")
    
    print("=" * 40)
    return afd_service

if __name__ == '__main__':
    import argparse
    import sys
    import os
    import importlib.util

    parser = argparse.ArgumentParser(
        description='Generador de lexer a partir de .yal y escáner opcional')
    parser.add_argument(
        '--yal',
        required=True,
        help='Ruta a un archivo .yal')
    parser.add_argument(
        '--scan_file',
        help='(Opcional) Ruta a un archivo para escaneo con el lexer generado')
    parser.add_argument(
        '--out', '-o',
        default='thelexer.py',
        help='Ruta de salida para el lexer generado (p.ej. thelexer.py)')
    args = parser.parse_args()

    # 1) Parsear .yal
    yal_info = parse_yal_file(args.yal)
    if yal_info is None:
        sys.exit(1)

    # 2) Generar el lexer Python
    generate_lexer_py(yal_info, args.out)
    print(f"✅ Lexer generado en {args.out}")

    # 3) Si se pidió escaneo, cargar y ejecutar entrypoint del lexer
    if args.scan_file:
        spec = importlib.util.spec_from_file_location(
            "thelexer", os.path.abspath(args.out))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        data = open(args.scan_file, encoding='utf-8').read()
        for tok, lex in mod.entrypoint(data):
            print(tok, lex)
