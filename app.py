from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService

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
    test_strings = [".**.Mama2"]
    print("\nProbando cadenas con el AFD minimizado:")
    for s in test_strings:
        result = afd_service.match(s)
        print(f"'{s}': {'Aceptada' if result else 'Rechazada'}")
    
    print("=" * 40)

if __name__ == '__main__':
    # Únicamente se procesará una lista de expresiones regulares (temporal).
    regex_list = [
        "(\.|\*)+([A-Za-z]*)[0-9]?"
    ]
    
    for regex in regex_list:
        process_regex(regex)
