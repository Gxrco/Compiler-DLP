# ————— HEADER —————
import myToken

class TokenInfo(tuple):
    def __new__(cls, token, lexeme, line): return (token, lexeme, line)

TRANSITIONS = {
    (1, 'o'): 2,
    (2, 'f'): 0,
    (3, 'e'): 1,
    (3, '*'): 0,
    (3, '5'): 4,
    (3, '/'): 0,
    (3, '8'): 4,
    (3, '2'): 4,
    (3, '4'): 4,
    (3, '1'): 4,
    (3, 'n'): 0,
    (3, '6'): 4,
    (3, ')'): 0,
    (3, '\\'): 0,
    (3, ' '): 0,
    (3, '3'): 4,
    (3, '0'): 4,
    (3, '+'): 0,
    (3, '-'): 0,
    (3, 't'): 0,
    (3, '9'): 4,
    (3, '('): 0,
    (3, '7'): 4,
    (4, '5'): 4,
    (4, '8'): 4,
    (4, '2'): 4,
    (4, '4'): 4,
    (4, '1'): 4,
    (4, '6'): 4,
    (4, '3'): 4,
    (4, '0'): 4,
    (4, '9'): 4,
    (4, '7'): 4,
}
INITIAL = 3
ACCEPTING = {

}

def tokenize(text: str):
    tokens = []
    line = 1
    pos = 0
    while pos < len(text):
        state = INITIAL
        last = None
        last_pos = pos
        i = pos
        while i < len(text) and (state, text[i]) in TRANSITIONS:
            state = TRANSITIONS[(state, text[i])]
            i += 1
            if state in ACCEPTING:
                last = state
                last_pos = i
        if last is None:
            raise SyntaxError(f"Unexpected character {text[pos]!r} at line {line}")
        lex = text[pos:last_pos]
        tokens.append(TokenInfo(ACCEPTING[last], lex, line))
        line += lex.count("\n")
        pos = last_pos
    return tokens

# ————— TRAILER —————

