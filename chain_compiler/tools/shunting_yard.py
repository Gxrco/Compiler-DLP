from chain_compiler.model.token import Token
from chain_compiler.model.operator import OPERATORS

def convert_to_postfix(tokens):
    """
    Convierte la lista de tokens (notación infix) a notación postfix usando el algoritmo Shunting Yard.

    Args:
        tokens (list): Lista de objetos Token.

    Returns:
        list: Lista de tokens en notación postfix.
    """
    output = []
    op_stack = []
    
    for token in tokens:
        if token.type in ['CHAR', 'CHAR_CLASS']:
            output.append(token)
        elif token.type in ['OPERATOR', 'QUANTIFIER']:
            # Determinar propiedades del operador actual
            if token.type == 'QUANTIFIER':
                current_op = OPERATORS['QUANTIFIER']
            else:
                if token.value not in OPERATORS:
                    raise ValueError(f"Operador desconocido: {token.value}")
                current_op = OPERATORS[token.value]
            # Mientras haya un operador en la pila con mayor o igual precedencia
            while op_stack:
                top = op_stack[-1]
                if top.type in ['OPERATOR', 'QUANTIFIER']:
                    if top.type == 'QUANTIFIER':
                        top_op = OPERATORS['QUANTIFIER']
                    else:
                        top_op = OPERATORS.get(top.value)
                        if top_op is None:
                            break
                    if ((current_op.associativity == 'left' and current_op.precedence <= top_op.precedence) or
                        (current_op.associativity == 'right' and current_op.precedence < top_op.precedence)):
                        output.append(op_stack.pop())
                    else:
                        break
                else:
                    break
            op_stack.append(token)
        elif token.type == 'LPAREN':
            op_stack.append(token)
        elif token.type == 'RPAREN':
            # Extraer operadores hasta encontrar el paréntesis izquierdo
            while op_stack and op_stack[-1].type != 'LPAREN':
                output.append(op_stack.pop())
            if op_stack and op_stack[-1].type == 'LPAREN':
                op_stack.pop()  # Eliminar el '('
            else:
                raise ValueError("Paréntesis desbalanceados")
    
    # Vaciar la pila de operadores
    while op_stack:
        top = op_stack.pop()
        if top.type in ['LPAREN', 'RPAREN']:
            raise ValueError("Paréntesis desbalanceados")
        output.append(top)
    
    return output