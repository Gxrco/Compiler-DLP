from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService
from file_processor import read_regex_from_file
import argparse

def process_regex(regex):
    print("Expresión regular:", regex)
    
    tokens = normalize_regex(regex)
    print("Tokens normalizados:", tokens)
    
    postfix = parse_tokens(tokens)
    print("Notación postfix:", postfix)
    
    ast = generate_ast(postfix)
    print("AST:")
    print(ast.pretty_print())
    
    # Construir y visualizar el AST
    ast_graph = build_ast_graph(ast)
    ast_graph.render('ast_graph', view=True)
    
    # Construir el DFA a partir del AST
    afd_service = AFDService()
    dfa = afd_service.build_dfa_from_ast(ast)
    
    normal_filename = f'dfa_normal_{regex.replace("?", "optional").replace("*", "star").replace("+", "plus").replace("|", "or")}'
    dfa.visualize(normal_filename)
    
    # Minimizar el DFA a través del servicio
    minimized_dfa = afd_service.minimize_dfa()
    
    minimized_filename = f'dfa_minimized_{regex.replace("?", "optional").replace("*", "star").replace("+", "plus").replace("|", "or")}'
    minimized_dfa.visualize(minimized_filename)
    
    
    # Probar algunas cadenas con el DFA minimizado
    # Esto será reemplazado por tests unitarios en el futuro.
    test_strings = [".**.Mama"]
    print("\nProbando cadenas con el AFD minimizado:")
    for s in test_strings:
        result = afd_service.match(s)
        print(f"'{s}': {'Aceptada' if result else 'Rechazada'}")
    
    print("=" * 40)

if __name__ == '__main__':
    # Set up argument parser for command line options
    parser = argparse.ArgumentParser(description='Process regular expressions directly or from a file.')
    parser.add_argument('--file', '-f', help='Path to file containing regex patterns')
    parser.add_argument('--regex', '-r', help='Direct regex pattern input')
    parser.add_argument('--concat', '-c', action='store_true', 
                        help='Concatenate all regex patterns into a single regex')
    args = parser.parse_args()
    
    regex_list = []
    
    # Process file input if provided
    if args.file:
        regex_list = read_regex_from_file(args.file)
        if not regex_list:
            print("No valid regex patterns found in file. Using default patterns.")
    
    # Process direct regex input if provided
    if args.regex:
        regex_list.append(args.regex)
    
    # Use default regex if no input was provided or if file was empty
    if not regex_list:
        regex_list = [
            "[a-zA-Z_]"
        ]
    
    # Handle concatenation if requested
    if args.concat and len(regex_list) > 1:
        # Simple concatenation of all regex patterns
        concatenated_regex = ''.join(regex_list)
        print(f"Concatenated regex: {concatenated_regex}")
        process_regex(concatenated_regex)
    else:
        # Process each regex separately
        for regex in regex_list:
            process_regex(regex)
