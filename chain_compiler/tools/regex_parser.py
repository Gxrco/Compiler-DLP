from chain_compiler.model.token import Token

def tokenize(regex):
    """
    Tokeniza una expresión regular en sus componentes básicos.
    Versión mejorada que maneja mejor clases de caracteres y caracteres especiales.
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
        '{': 'SPECIAL_CHAR',
        '}': 'SPECIAL_CHAR',
        '#': 'SPECIAL_OPERATOR'
    }

    # Preprocesamiento para el caso "#" y [a-zA-Z0-9 ]+ juntos
    # Convertirlos en '#" [a-zA-Z0-9 ]+
    processed_regex = regex
    processed_regex = processed_regex.replace('("#" ', '("#" ')
    
    regex = processed_regex
    
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
            i += 1
            
        # Manejar clases de caracteres como [a-z]
        elif char == '[':
            # Encuentre el cierre de corchete correspondiente
            j = i + 1
            char_class = '['
            while j < len(regex) and regex[j] != ']':
                if regex[j] == '\\' and j + 1 < len(regex):
                    char_class += regex[j:j+2]
                    j += 2
                else:
                    char_class += regex[j]
                    j += 1
            
            if j >= len(regex):
                # Si no encontramos el cierre, tratamos el '[' como un carácter literal
                token = Token('CHAR', '[')
                i += 1
            else:
                # Incluir el cierre en la clase
                char_class += ']'
                token = Token('CHAR_CLASS', char_class)
                i = j + 1
        
        # Manejar marcador de token (#TOKEN)
        elif char == '#' and i+1 < len(regex):
            j = i + 1
            token_name = ''
            while j < len(regex) and (regex[j].isalnum() or regex[j] == '_'):
                token_name += regex[j]
                j += 1
            
            if token_name:
                token = Token('TOKEN_MARKER', f"#{token_name}")
                i = j
            else:
                token = Token('CHAR', '#')
                i += 1
        
        # Manejar operadores y otros caracteres especiales
        elif char in special_chars:
            token = Token(special_chars[char], char)
            i += 1
        
        # Caracteres normales
        else:
            token = Token('CHAR', char)
            i += 1
        
        # Insertar operador de concatenación implícito si es necesario
        if previous_token is not None:
            if can_concat_prev(previous_token) and can_concat_current(token.type):
                tokens.append(Token('OPERATOR', '&'))
        
        tokens.append(token)
        previous_token = token
    
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