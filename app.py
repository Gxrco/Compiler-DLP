import argparse
import re
from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService
from file_processor import read_regex_from_file
from chain_compiler.tools.yal_parser import parse_yal_file
from chain_compiler.tools.super_regex_builder import build_super_regex

def scan_input_file(filepath, yal_rules):
    patterns = []
    for regex, tok in yal_rules:
        try:
            pat = re.compile(rf'^{regex.strip()}')
        except re.error:
            pat = re.compile(rf'^{re.escape(regex.strip())}')
        patterns.append((pat, tok))

    symbol_table = []
    with open(filepath, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            pos = 0
            while pos < len(line):
                best = None
                for pat, tok in patterns:
                    m = pat.match(line[pos:])
                    if m and (not best or len(m.group(0)) > len(best[0])):
                        best = (m.group(0), tok)
                if best:
                    lex, token = best
                    if token not in ("lexbuf", "EOL"):
                        symbol_table.append((lineno, token, lex))
                    pos += len(lex)
                else:
                    pos += 1

    # Imprimir tabla formateada
    print("\nTabla de símbolos:")
    header = ("Line", "Token", "Lexeme")
    widths = [max(len(str(r[i])) for r in ([header] + symbol_table)) for i in range(3)]
    print(f"{header[0]:<{widths[0]}}  {header[1]:<{widths[1]}}  {header[2]:<{widths[2]}}")
    print("-" * (sum(widths) + 4))
    for line, token, lex in symbol_table:
        print(f"{line:<{widths[0]}}  {token:<{widths[1]}}  {lex:<{widths[2]}}")

        

def process_regex(super_regex, test_strings=None):
    """
    Procesa una expresión regular, construye el AST, el DFA normal y minimizado.
    
    Args:
        super_regex (str): La expresión regular a procesar
        test_strings (list): Lista opcional de cadenas para probar
    
    Returns:
        AFDService: La instancia del servicio AFD con el DFA construido
    """
    print("Expresión regular:", super_regex)
    
    # Tokenizar la regex
    tokens = normalize_regex(super_regex)
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
    safe_regex = super_regex.replace("?", "optional").replace("*", "star").replace("+", "plus").replace("|", "or")
    safe_regex = re.sub(r'[^\w\-_]', '', safe_regex)
    normal_filename = f'dfa_normal_{safe_regex[:30]}'
    dfa.visualize(normal_filename)
    
    # Minimizar el DFA
    minimized_dfa = afd_service.minimize_dfa()
    
    # Generar un nombre de archivo único para el DFA minimizado
    minimized_filename = f'dfa_minimized_{safe_regex[:30]}'
    minimized_dfa.visualize(minimized_filename)
    
    # Probar cadenas si se proporcionan
    if test_strings:
        print("\nProbando cadenas con el AFD minimizado:")
        for s in test_strings:
            result = afd_service.match(s)
            status = 'Aceptada' if result else 'Rechazada'
            token = f" (Token: {result})" if result else ""
            print(f"'{s}': {status}{token}")
    
    return afd_service

def process_yal_file(path, scan_file=None, test_strings=None):
    """
    Procesa un archivo .yal y opcionalmente escanea un archivo de entrada.
    
    Args:
        path (str): Ruta al archivo .yal
        scan_file (str): Ruta opcional al archivo a escanear
        test_strings (list): Lista opcional de cadenas para probar
    """
    info = parse_yal_file(path)
    if not info:
        print("Error al parsear el archivo .yal")
        return
    
    print("Header:\n", info.get("header", ""))
    print("Rule:", info.get("rule", ""))
    print("Alternativas:")
    for r, a in info.get("alternatives", []): 
        print(f"  {r} => {a}")
    print("Trailer:\n", info.get("trailer", ""))
    
    # Extraer los tokens de las acciones
    yal_rules = []
    for regex, action in info.get("alternatives", []):
        # Extraer token: primero busca return "TOKEN" o return 'TOKEN'
        m = re.search(r'return\s+[\'"]([^\'"]+)[\'"]', action)
        if m:
            token = m.group(1)
        elif "return" in action:
            # Si no hay comillas, toma la función (int, etc.) como token
            m = re.search(r'return\s*([A-Za-z_]\w*)', action)
            token = m.group(1).upper() if m else "UNKNOWN"
        elif "raise" in action:
            token = "EOF"
        else:
            token = "UNKNOWN"
        
        # Limpiar el patrón — quitar comillas internas, mantener clases intactas
        clean = regex.strip().replace("'", "").replace('"', "")
        yal_rules.append((clean, token))
    
    # Construir el super-regex
    super_regex = build_super_regex(info.get("alternatives", []))
    print("\nSuper-regex construido:", super_regex)
    
    # Procesar el super-regex y generar visualizaciones
    afd_service = process_regex(super_regex, test_strings)
    
    # Escanear archivo de entrada si se proporciona
    if scan_file:
        scan_input_file(scan_file, yal_rules)
    
    return afd_service

if __name__ == '__main__':
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Procesador de archivos YAL y escáner.')
    parser.add_argument('--yal', help='Ruta a un archivo .yal')
    parser.add_argument('--scan_file', help='Ruta a un archivo de entrada para escaneo')
    parser.add_argument('--test', '-t', nargs='+', help='Cadenas de prueba para el AFD')
    args = parser.parse_args()
    
    # Configurar cadenas de prueba
    test_strings = args.test if args.test else None
    
    if args.yal:
        process_yal_file(args.yal, args.scan_file, test_strings)
    else:
        print("Use --yal <archivo>.")