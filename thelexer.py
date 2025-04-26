token_names = ['COMMENT', 'IF', 'ELSE', 'WHILE', 'EQUALS', 'NOTEQUAL', 'GREATEREQ', 'LESSEQ', 'LESS', 'GREATER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'LBRACKET', 'LBRACE', 'RBRACE', 'COLON', 'SEMICOLON', 'ASSIGN', 'COMMA', 'ID', 'NUMBER', 'WHITESPACE']
super_regex = r'''(\#[^\n]*)|(if)|(else)|(while)|(==)|(!=)|(>=)|(<=)|(<)	|(>)\n|(\+)|(\-)|(\*)|(/)|(\()|(\))|(\[)|(")|(\})|(:)|(;)|(=)|(,)|([a-zA-Z][a-zA-Z0-9]*)|([0-9]+)|([ \t\n\r])'''

from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser     import parse_tokens
from chain_compiler.ast_service import generate_ast
from afd_compiler.service       import AFDService

afd_service  = AFDService()
tokens_norm  = normalize_regex(super_regex)
postfix      = parse_tokens(tokens_norm)
ast          = generate_ast(postfix)
dfa          = afd_service.build_dfa_from_ast(ast, token_names)
afd_service.minimize_dfa()

def entrypoint(buffer: str):
    """Escanea el buffer y devuelve lista de (token, lexeme),
       descartando espacios y comentarios."""
    tokens = afd_service.scan_input(buffer)
    return [(tok,lex) for tok,lex in tokens
            if tok not in ('WHITESPACE','COMMENT')]

def process_token(token, lexeme):
    return (token, lexeme)

if __name__ == '__main__':
    import sys
    data = sys.stdin.read()
    for tok,lex in entrypoint(data):
        print(tok, lex)
