token_names = ['COMMENT', 'IF', 'ELSE', 'WHILE', 'EQUALS', 'NOTEQUAL', 'GREATEREQ', 'LESSEQ', 'LESS', 'GREATER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'LBRACKET', 'LBRACE', 'RBRACE', 'COLON', 'SEMICOLON', 'ASSIGN', 'COMMA', 'ID', 'NUMBER', 'WHITESPACE']
super_regex = '(\\#[^\\n]*)\x01|(if)\x02|(else)\x03|(while)\x04|(==)\x05|(!=)\x06|(>=)\x07|(<=)\x08|(<)\t|(>)\n|(\\+)\x0b|(\\-)\x0c|(\\*)\r|(/)\x0e|(\\()\x0f|(\\))\x10|(\\[)\x11|(")\x12|(\\})\x13|(:)\x14|(;)\x15|(=)\x16|(,)\x17|([a-zA-Z][a-zA-Z0-9]*)\x18|([0-9]+)\x19|([ \\t\\n\\r])\x1a'

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
       descartando espacios y comentarios. Añade '#' al final como sentinel."""
    # agregamos '#' para que cada patrón dispare su marcador de token al terminar
    tokens = afd_service.scan_input(buffer + '#')
    return [(tok,lex) for tok,lex in tokens
            if tok not in ('WHITESPACE','COMMENT')]

def process_token(token, lexeme):
    return (token, lexeme)

if __name__ == '__main__':
    import sys
    data = sys.stdin.read()
    for tok,lex in entrypoint(data):
        print(tok, lex)
