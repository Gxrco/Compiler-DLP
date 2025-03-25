from chain_compiler.model.token import Token

def tokenize(regex):
    """
    Tokeniza una expresión regular en sus componentes básicos.
    Maneja correctamente los operadores, caracteres especiales, clases de caracteres, etc.
    """
    tokens = []
    i = 0
    previous_token = None

    def can_concat_prev(token):
        """Verifica si el token anterior puede concatenarse con el actual."""
        return token.type in ['CHAR', 'CHAR_CLASS', 'RPAREN'] or \
               (token.type == 'OPERATOR' and token.value in ['*', '+', '?'])
    
    def can_concat_current(token_type):
        """Verifica si el token actual puede concatenarse con el anterior."""
        return token_type in ['CHAR', 'CHAR_CLASS', 'LPAREN']

    special_chars = {
        '*': 'OPERATOR',
        '+': 'OPERATOR',
        '?': 'OPERATOR',
        '|': 'OPERATOR',
        '(': 'LPAREN',
        ')': 'RPAREN',
        '[': 'CHAR_CLASS_START',
        ']': 'CHAR_CLASS_END',
        '#': 'SPECIAL_OPERATOR'  # Añadimos el operador de diferencia
    }

    while i < len(regex):
        char = regex[i]
        token = None

        # Manejar escape de caracteres
        if char == '\\':
            i += 1
            if i >= len(regex):
                raise ValueError("Escape incompleto al final de la expresión")
            escaped_char = regex[i]
            token = Token('CHAR', escaped_char)
        # Manejar clases de caracteres
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
        # Manejar operadores y otros caracteres especiales
        elif char in special_chars:
            if char == '#' and i+1 < len(regex) and regex[i+1] != ' ':
                # Si # es seguido inmediatamente por otro carácter que no es espacio,
                # podría ser un token especial (como en regex)#TOKEN
                j = i + 1
                token_name = ''
                while j < len(regex) and regex[j].isalnum():
                    token_name += regex[j]
                    j += 1
                if token_name:
                    token = Token('TOKEN_MARKER', f"#{token_name}")
                    i = j - 1
                else:
                    token = Token(special_chars[char], char)
            else:
                token = Token(special_chars[char], char)
        # Caracteres normales
        else:
            token = Token('CHAR', char)
        
        # Insertar operador de concatenación implícito si es necesario
        if previous_token is not None:
            if can_concat_prev(previous_token) and can_concat_current(token.type):
                tokens.append(Token('OPERATOR', '&'))
        
        tokens.append(token)
        previous_token = token
        i += 1
    
    return tokens

def expand_char_class(class_str):
    """
    Expande una clase de caracteres en una expresión regular.
    Por ejemplo, [a-z] se convierte en (a|b|c|...|z)
    """
    content = class_str[1:-1]
    is_negated = content.startswith('^')
    if is_negated:
        content = content[1:]

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

    # Para clases negadas, necesitaríamos un enfoque diferente en regex
    if is_negated:
        return f"[^{''.join(elements)}]"
    else:
        # Para clases pequeñas, usar OR explícito
        if len(elements) <= 5:
            return "(" + "|".join(elements) + ")"
        # Para clases grandes, mantener la sintaxis de clase de caracteres
        else:
            return class_str