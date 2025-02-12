from chain_compiler.model.token import Token

def tokenize(regex):
    """
    Convierte una expresión regular en una lista de tokens, insertando operadores de concatenación explícitos.
    Soporta caracteres escapados, clases de caracteres y cuantificadores.

    Args:
        regex (str): La expresión regular de entrada.

    Returns:
        list: Lista de objetos Token.
    """
    tokens = []
    i = 0
    previous_token = None

    def can_concat_prev(token):
        return token.type in ['CHAR', 'CHAR_CLASS', 'RPAREN', 'QUANTIFIER'] or \
               (token.type == 'OPERATOR' and token.value in ['*', '+', '?'])
    
    def can_concat_current(token_type):
        return token_type in ['CHAR', 'CHAR_CLASS', 'LPAREN']

    while i < len(regex):
        char = regex[i]
        token = None

        if char == '\\':
            i += 1
            if i >= len(regex):
                raise ValueError("Secuencia de escape incompleta al final de la expresión")
            escaped_char = regex[i]
            token = Token('CHAR', '\\' + escaped_char)
        elif char == '[':
            # Clase de caracteres: se captura desde '[' hasta ']'
            j = i + 1
            char_class = '['
            if j < len(regex) and regex[j] == '^':  
                char_class += '^'
                j += 1
            while j < len(regex) and regex[j] != ']':
                if regex[j] == '\\':
                    if j + 1 < len(regex):
                        char_class += regex[j:j+2]
                        j += 2
                        continue
                    else:
                        raise ValueError("Secuencia de escape incompleta en clase de caracteres")
                else:
                    char_class += regex[j]
                    j += 1
            if j >= len(regex) or regex[j] != ']':
                raise ValueError("Clase de caracteres no terminada")
            char_class += ']'
            token = Token('CHAR_CLASS', char_class)
            i = j  
        elif char == '{':
            # Cuantificador: se captura desde '{' hasta '}'
            j = i + 1
            quant = '{'
            while j < len(regex) and regex[j] != '}':
                quant += regex[j]
                j += 1
            if j >= len(regex) or regex[j] != '}':
                raise ValueError("Cuantificador no terminado")
            quant += '}'
            token = Token('QUANTIFIER', quant)
            i = j  
        elif char == '(':
            token = Token('LPAREN', char)
        elif char == ')':
            token = Token('RPAREN', char)
        elif char in ['|', '*', '+', '?']:
            token = Token('OPERATOR', char)
        else:
            # Cualquier otro carácter (incluyendo el literal '.' que significa “cualquier carácter”).
            token = Token('CHAR', char)
        
        # Inserta operador de concatenación explícito ('&') cuando corresponda.
        if previous_token is not None:
            if can_concat_prev(previous_token) and can_concat_current(token.type):
                tokens.append(Token('OPERATOR', '&'))
        
        tokens.append(token)
        previous_token = token
        i += 1
    
    return tokens