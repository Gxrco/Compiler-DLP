from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService
from file_processor import read_regex_from_file
import argparse
from chain_compiler.tools.yal_parser import parse_yal_file
import re
from chain_compiler.tools.super_regex_builder import build_super_regex


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

def process_yal_file(filepath, test_strings=None):
    """
    Procesa un archivo .yal, extrae las reglas y construye el super-regex.
    
    Args:
        filepath (str): Ruta al archivo .yal
        test_strings (list): Lista opcional de cadenas para probar
    """
    print(f"Procesando archivo YAL: {filepath}")
    
    # Parsear el archivo .yal
    yal_info = parse_yal_file(filepath)
    if not yal_info:
        print("Error al parsear el archivo .yal")
        return
    
    print("Definiciones encontradas:")
    for name, definition in yal_info['definitions'].items():
        print(f"  {name} = {definition}")
    
    print("\nReglas encontradas:")
    for regex, action in yal_info['rules']:
        print(f"  {regex} => {action}")
    
    # Construir el super-regex
    super_regex = build_super_regex(yal_info['rules'])
    print("\nSuper-regex construido:", super_regex)
    
    # Procesar el super-regex
    afd_service = process_regex(super_regex, test_strings)
    
    # Devolver el servicio AFD por si se necesita para más pruebas
    return afd_service

if __name__ == '__main__':
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Procesador de expresiones regulares y archivos YAL.')
    parser.add_argument('--yal', help='Ruta a un archivo .yal')
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
        process_yal_file(args.yal, test_strings)
        exit(0)
    
    # Procesar regex desde un archivo o entrada directa
    regex_list = []
    
    if args.file:
        regex_list = read_regex_from_file(args.file)
        if not regex_list:
            print("No se encontraron patrones regex válidos en el archivo. Usando patrones predeterminados.")
    
    if args.regex:
        regex_list.append(args.regex)
    
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