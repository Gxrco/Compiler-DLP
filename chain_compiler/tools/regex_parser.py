from chain_compiler.model.token import Token

def tokenize(regex):
    tokens = []
    i = 0
    previous_token = None

    def can_concat_prev(token):
        return token.type in ['CHAR', 'CHAR_CLASS', 'RPAREN', 'QUANTIFIER'] or \
               (token.type == 'OPERATOR' and token.value in ['*', '+', '?'])
    
    def can_concat_current(token_type):
        return token_type in ['CHAR', 'CHAR_CLASS', 'LPAREN']

    special_chars = {
        '*': 'OPERATOR',
        '+': 'OPERATOR',
        '?': 'OPERATOR',
        '|': 'OPERATOR',
        '(': 'LPAREN',
        ')': 'RPAREN',
        '[': 'CHAR_CLASS_START',
        ']': 'CHAR_CLASS_END'
    }

    while i < len(regex):
        char = regex[i]
        token = None

        if char == '\\':
            i += 1
            if i >= len(regex):
                raise ValueError("Escape incompleto al final de la expresión")
            escaped_char = regex[i]
            token = Token('CHAR', escaped_char)
        elif char == '[':
            j = i + 1
            char_class = '['
            while j < len(regex) and regex[j] != ']':
                if regex[j] == '\\' and j + 1 < len(regex):
                    char_class += regex[j:j+2]
                    j += 2
                else:
                    char_class += regex[j]
                    j += 1
            if j >= len(regex) or regex[j] != ']':
                raise ValueError("Clase de caracteres no terminada")
            char_class += ']'
            token = Token('CHAR_CLASS', char_class)
            i = j
        elif char in special_chars:
            token = Token(special_chars[char], char)
        else:
            token = Token('CHAR', char)
        
        if previous_token is not None:
            if can_concat_prev(previous_token) and can_concat_current(token.type):
                tokens.append(Token('OPERATOR', '&'))
        
        tokens.append(token)
        previous_token = token
        i += 1
    
    return tokens

def expand_char_class(class_str):
    content = class_str[1:-1]
    if content.startswith('^'):
        return class_str

    elements = []
    i = 0
    while i < len(content):
        if i + 2 < len(content) and content[i+1] == '-':
            start = content[i]
            end = content[i+2]
            for c in range(ord(start), ord(end)+1):
                elements.append(chr(c))
            i += 3
        else:
            elements.append(content[i])
            i += 1
    return "(" + "|".join(elements) + ")"