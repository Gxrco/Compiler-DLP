from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService
from file_processor import read_regex_from_file
import argparse
from chain_compiler.tools.yal_parser import parse_yal_file
import re
from chain_compiler.tools.super_regex_builder import build_super_regex

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
    print("Expresión regular:", regex)
    
    # Tokenizar la regex
    tokens = normalize_regex(regex)
    print("Tokens normalizados:", tokens)
    
    # Convertir a notación postfix
    postfix = parse_tokens(tokens)
    print("Notación postfix:", postfix)
    
    # Generar el AST
    ast = generate_ast(postfix)
    #print("AST:")
    #print(ast.pretty_print())
    
    # Construir y visualizar el AST
    ast_graph = build_ast_graph(ast)
    ast_graph.render('ast_graph', view=False)
    
    # Construir el DFA a partir del AST, indicándole que ya contiene marcadores
    afd_service = AFDService()
    dfa = afd_service.build_dfa_from_ast(ast, already_marked=True)
    
    safe_regex = regex.replace("?", "optional").replace("*", "star").replace("+", "plus").replace("|", "or")
    safe_regex = re.sub(r'[^\w\-_]', '', safe_regex)
    normal_filename = f'dfa_normal_{safe_regex[:30]}'
    dfa.visualize(normal_filename)
    
    minimized_dfa = afd_service.minimize_dfa()
    minimized_filename = f'dfa_minimized_{safe_regex[:30]}'
    minimized_dfa.visualize(minimized_filename)
    
    if test_strings is None:
        test_strings = ["bcdfghjklmnpqrstvwxyz"]
    
    print("\nProbando cadenas con el AFD minimizado:")
    for s in test_strings:
        result = afd_service.match(s)
        status = 'Aceptada' if result else 'Rechazada'
        token_str = f" (Token: {result})" if result else ""
        print(f"'{s}': {status}{token_str}")
    
    print("=" * 40)
    return afd_service


def process_yal_file(filepath, test_strings=None):
    """
    Procesa un archivo .yal, extrae los bloques de header, la regla principal y las alternativas,
    y construye el super-regex.
    
    Args:
        filepath (str): Ruta al archivo .yal.
        test_strings (list): Lista opcional de cadenas para probar.
    """
    print(f"Procesando archivo YAL: {filepath}")
    
    # Parsear el archivo .yal usando el nuevo parser
    yal_info = parse_yal_file(filepath)
    if not yal_info:
        print("Error al parsear el archivo .yal")
        return
    
    # Mostrar el header
    if yal_info.get("header"):
        print("Header:")
        print(yal_info["header"])
    
    # Mostrar la regla principal
    if yal_info.get("rule"):
        print("Regla principal encontrada:", yal_info["rule"])
    
    # Mostrar las alternativas encontradas
    print("\nAlternativas encontradas:")
    for regex, action in yal_info.get("alternatives", []):
        print(f"  {regex} => {action}")
    
    # Mostrar el trailer si existe
    if yal_info.get("trailer"):
        print("\nTrailer:")
        print(yal_info["trailer"])
    
    # Construir el super-regex a partir de las alternativas
    super_regex = build_super_regex(yal_info.get("alternatives", []))
    print("\nSuper-regex construido:", super_regex)
    
    # Procesar el super-regex (construir AST, DFA, etc.)
    afd_service = process_regex(super_regex, test_strings)
    
    # Devolver el servicio AFD por si se necesita para más pruebas
    return afd_service

if __name__ == '__main__':
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Procesador de expresiones regulares y archivos YAL.')
    parser.add_argument('--yal', help='Ruta a un archivo .yal')
    parser.add_argument('--scan_file', help='Ruta a un archivo de entrada para escaneo')
    parser.add_argument('--file', '-f', help='Ruta a un archivo con patrones regex')
    parser.add_argument('--regex', '-r', help='Expresión regular directa')
    parser.add_argument('--test', '-t', nargs='+', help='Cadenas de prueba')
    parser.add_argument('--concat', '-c', action='store_true', 
                        help='Concatenar todos los patrones regex en uno solo')
    args = parser.parse_args()
    
    # Configurar cadenas de prueba
    test_strings = args.test if args.test else None
    
    # Procesar un archivo .yal si se proporciona
    if args.yal:
        afd_service = process_yal_file(args.yal, test_strings)

        if args.scan_file and afd_service:
            scan_input_file(args.scan_file, afd_service)
        
        exit(0)
    
    # Procesar regex desde un archivo o entrada directa
    regex_list = []
    
    if args.file:
        regex_list = read_regex_from_file(args.file)
        if not regex_list:
            print("No se encontraron patrones regex válidos en el archivo. Usando patrones predeterminados.")
    
    if args.regex:
        regex_list.append(args.regex)
    
    if args.scan_file:
        # Se asume que el DFA se construye a partir de la primera regex o de un archivo .yal.
        # Aquí se utiliza el primer regex de la lista; ajusta según tus necesidades.
        afd_service = process_regex(regex_list[0], test_strings)
        scan_input_file(args.scan_file, afd_service)
        exit(0)
    
    # Usar regex predeterminado si no se proporciona entrada
    if not regex_list:
        regex_list = ["[a-z]#[aeiou]+"]
    
    # Manejar la concatenación si se solicita
    if args.concat and len(regex_list) > 1:
        concatenated_regex = ''.join(regex_list)
        print(f"Regex concatenado: {concatenated_regex}")
        process_regex(concatenated_regex, test_strings)
    else:
        # Procesar cada regex por separado
        for regex in regex_list:
            process_regex(regex, test_strings)
