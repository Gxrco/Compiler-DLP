class Token:
    """
    Clase que representa un token en la expresión regular.
    
    Atributos:
        type (str): El tipo de token (por ejemplo, 'CHAR', 'OPERATOR', 'LPAREN', 'RPAREN').
        value (str): El valor literal del token.
    """
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"