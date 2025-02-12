# app.py
from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService

def process_regex(regex):
    print("Expresión regular:", regex)
    
    # Generar AST
    tokens = normalize_regex(regex)
    print("Tokens normalizados:", tokens)
    
    postfix = parse_tokens(tokens)
    print("Notación postfix:", postfix)
    
    ast = generate_ast(postfix)
    print("AST:")
    print(ast.pretty_print())
    
    graph = build_ast_graph(ast)
    graph.render('ast_graph', view=True)
    
    afd_service = AFDService()
    dfa = afd_service.build_dfa_from_ast(ast)
    
    dfa.visualize(f'dfa_graph_{regex.replace("?", "optional").replace("*", "star").replace("+", "plus").replace("|", "or")}')
    
    dfa_info = afd_service.get_dfa_info()
    print("\nInformación del AFD:")
    print(f"Número de estados: {dfa_info['states_count']}")
    print(f"Alfabeto: {dfa_info['alphabet']}")
    print(f"Número de transiciones: {dfa_info['transitions_count']}")
    print(f"Estados de aceptación: {dfa_info['accepting_states_count']}")
    
    # Probar algunas cadenas
    test_strings = ["ac", "acc", "bc", "bcccc", "ab", "a", "b"]
    print("\nProbando cadenas:")
    for s in test_strings:
        result = afd_service.match(s)
        print(f"'{s}': {'Aceptada' if result else 'Rechazada'}")
    
    print("="*40)

if __name__ == '__main__':
    regex_list = [
        r"(a|b)c+",
    ]
    
    for regex in regex_list:
        process_regex(regex)