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
    for regex, tok, func in yal_rules:
        pat_text = regex.strip()
        try:
            patterns.append((re.compile(rf'^{pat_text}'), tok, func))
        except re.error:
            patterns.append((re.compile(rf'^{re.escape(pat_text)}'), tok, func))
    table = []
    with open(filepath, encoding='utf-8') as f:
        for lineno, line in enumerate(f,1):
            pos = 0
            while pos < len(line):
                best = None
                for pat, tok, func in patterns:
                    m = pat.match(line[pos:])
                    if m and (not best or len(m.group(0)) > len(best[0])):
                        best = (m.group(0), tok, func)
                if best:
                    lex, tok, func = best
                    value = func(lex)
                    table.append({"line":lineno, "token":tok, "lexeme":lex, "value":value})
                    pos += len(lex)
                else:
                    pos += 1
    print("\nTabla de símbolos:")
    for entry in table:
        print(entry)

        

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


def make_action(action):
    action = action.strip()

    # Caso especial: devolver el propio lexema
    if re.match(r'return\s+lexbuf', action):
        return lambda lxm: lxm

    # Extraer lo que sigue a return
    m = re.search(r'return\s+(.+?);?$', action)
    if m:
        expr = m.group(1).strip()

        # Si es un identificador simple (token name), devuélvelo como string
        if re.fullmatch(r'[A-Za-z_]\w*', expr):
            return lambda lxm, t=expr: t

        # De lo contrario, compile como expresión Python (e.g. int(lxm))
        code = compile(f"lambda lxm: {expr}", "<action>", "eval")
        return eval(code)

    # Raise EOF
    if "raise" in action:
        return lambda lxm: (_ for _ in ()).throw(Exception("EOF"))

    return lambda lxm: None



def process_yal_file(path, scan_file=None, test_strings=None):
    info = parse_yal_file(path)
    yal_rules = []
    for regex, action in info["alternatives"]:
        # Primero busca return "TOKEN" o return 'TOKEN'
        m = re.search(r'return\s+[\'"]([^\'"]+)[\'"]', action)
        if m:
            token = m.group(1)
        else:
            # Si no hay comillas, capturar palabra tras return
            m2 = re.search(r'return\s+([A-Za-z_]\w*)', action)
            if m2:
                token = m2.group(1)
            elif "raise" in action:
                token = "EOF"
            else:
                token = "UNKNOWN"

        func = make_action(action)
        clean = regex.strip().replace("'", "").replace('"', "")
        yal_rules.append((clean, token, func))
        
    super_regex = build_super_regex(info["alternatives"])
    afd = process_regex(super_regex)
    if scan_file:
        scan_input_file(scan_file, yal_rules)
    return afd



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