import re

patterns = [
    (re.compile(r'if'), 'IF'),
    (re.compile(r'else'), 'ELSE'),
    (re.compile(r'while'), 'WHILE'),
    (re.compile(r'=='), 'EQUALS'),
    (re.compile(r'!='), 'NOTEQUAL'),
    (re.compile(r'>='), 'GREATEREQ'),
    (re.compile(r'<='), 'LESSEQ'),
    (re.compile(r'<'), 'LESS'),
    (re.compile(r'>'), 'GREATER'),
    (re.compile(r'\+'), 'PLUS'),
    (re.compile(r'\-'), 'MINUS'),
    (re.compile(r'\*'), 'TIMES'),
    (re.compile(r'/'), 'DIVIDE'),
    (re.compile(r'\('), 'LPAREN'),
    (re.compile(r'\)'), 'RPAREN'),
    (re.compile(r'\['), 'LBRACKET'),
    (re.compile(r'"'), 'LBRACE'),
    (re.compile(r'\}'), 'RBRACE'),
    (re.compile(r':'), 'COLON'),
    (re.compile(r';'), 'SEMICOLON'),
    (re.compile(r'='), 'ASSIGN'),
    (re.compile(r','), 'COMMA'),
    (re.compile(r'[a-zA-Z][a-zA-Z0-9]*'), 'ID'),
    (re.compile(r'[0-9]+'), 'NUMBER'),
]

def entrypoint(buffer: str):
    '''Escanea el buffer y devuelve lista de (token, lexeme)'''
    pos = 0
    tokens = []
    length = len(buffer)
    while pos < length:
        best = ('', None)
        for pat, tok in patterns:
            m = pat.match(buffer, pos)
            if m:
                lex = m.group(0)
                if len(lex) > len(best[0]):
                    best = (lex, tok)
        if best[1]:
            tokens.append((best[1], best[0]))
            pos += len(best[0])
        else:
            # Carácter no reconocido → ERROR
            tokens.append(('ERROR', buffer[pos]))
            pos += 1
    return tokens

def process_token(token, lexeme):
    return (token, lexeme)

if __name__ == '__main__':
    import sys
    data = sys.stdin.read()
    for tok, lex in entrypoint(data):
        print(tok, lex)
