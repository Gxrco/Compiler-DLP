token_names = ['COMMENT', 'IF', 'ELSE', 'WHILE', 'EQUALS', 'NOTEQUAL', 'GREATEREQ', 'LESSEQ', 'LESS', 'GREATER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COLON', 'SEMICOLON', 'ASSIGN', 'COMMA', 'ID', 'NUMBER', 'WHITESPACE', 'WHITESPACE', 'WHITESPACE']
super_regex = '("#"[^\\n]*\\n)\x01|(if)\x02|(else)\x03|(while)\x04|(==)\x05|(!=)\x06|(>=)\x07|(<=)\x08|(<)\t|(>)\n|(\\+)\x0b|(\\-)\x0c|(\\*)\r|(/)\x0e|(\\()\x0f|(\\))\x10|(\\[)\x11|(\\])\x12|()\x13|(\\})\x14|(:)\x15|(;)\x16|(=)\x17|(,)\x18|([a-zA-Z_][a-zA-Z0-9_]*)\x19|([0-9]+)\x1a|([ \\t]+)\x1b|(\\n)\x1c|(\\r\\n)\x1d|(\x00)'

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

SENTINEL = '\x00'

def entrypoint(buffer: str):
    """Escanea el buffer y devuelve lista de (token, lexeme),
       descartando espacios, comentarios y errores léxicos."""
    # agregamos el sentinel para delimitar el final
    tokens = afd_service.scan_input(buffer + SENTINEL)
    return [(tok, lex) for tok, lex in tokens
            if tok not in ('WHITESPACE','COMMENT','ERROR')]

def process_token(token, lexeme):
    return (token, lexeme)

if __name__ == '__main__':
    import sys
    data = sys.stdin.read()
    for tok, lex in entrypoint(data):
        print(tok, lex)
