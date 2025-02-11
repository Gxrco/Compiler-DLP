from regex_normalizer.model.token import Token

def tokenize(regex):
    """
    Convierte una expresión regular en una lista de tokens, insertando operadores de concatenación explícitos.
    
    Args:
        regex (str): La expresión regular de entrada.
    
    Returns:
        list: Lista de objetos Token.
    """
    tokens = []
    special_chars = {'(', ')', '*', '+', '?', '|'}
    previous_token = None
    
    for char in regex:
        if char in special_chars:
            if char == '(':
                token = Token('LPAREN', char)
            elif char == ')':
                token = Token('RPAREN', char)
            else:
                token = Token('OPERATOR', char)
        else:
            token = Token('CHAR', char)
        
        if previous_token is not None:
            if (previous_token.type in ['CHAR', 'RPAREN'] or 
                (previous_token.type == 'OPERATOR' and previous_token.value in ['*', '+', '?'])):
                if token.type in ['CHAR', 'LPAREN']:
                    tokens.append(Token('OPERATOR', '.'))
        
        tokens.append(token)
        previous_token = token
    
    return tokens
