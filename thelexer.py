from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast
from afd_compiler.service import AFDService

# Super-regex construido en generación
super_regex = r'''([  \t])#lexbuf|([\n])#EOL|([0-9]+)#intlxm|(\+)#PLUS|(\-)#MINUS|(\*)#TIMES|(/)#DIV|(\()#LPAREN|(\))#RPAREN|(eof)#EOF'''

# Inicialización del AFD en tiempo de carga
afd_service = AFDService()
tokens_norm = normalize_regex(super_regex)
postfix = parse_tokens(tokens_norm)
ast = generate_ast(postfix)
dfa = afd_service.build_dfa_from_ast(ast)
afd_service.minimize_dfa()

def entrypoint(buffer: str):
    '''Escanea el buffer y devuelve lista de (token, lexeme) usando el DFA interno'''
    return afd_service.scan_input(buffer)

if __name__ == '__main__':
    import sys
    data = sys.stdin.read()
    for tok, lex in entrypoint(data):
        print(tok, lex)
