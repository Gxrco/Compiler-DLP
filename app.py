# main.py
from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast
from chain_compiler.ast_service import build_ast_graph


def process_regex(regex):
    print("Expresión regular:", regex)
    
    tokens = normalize_regex(regex)
    print("Tokens normalizados:", tokens)
    
    postfix = parse_tokens(tokens)
    print("Notación postfix:", postfix)
    
    ast = generate_ast(postfix)
    print("AST:")
    print(ast.pretty_print())
    print("="*40)
    
    graph = build_ast_graph(ast)
    graph.render('ast_graph', view=True)

if __name__ == '__main__':
    regex_list = [
        r"(\W|^)[\w.\-]{0,25}@(yahoo|hotmail|gmail)\.com(\W|$)",
        r"(a|b)c+",
        r"ab?c"
    ]
    
    for regex in regex_list:
        process_regex(regex)
    
