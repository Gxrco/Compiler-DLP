from chain_compiler.model.token import Token
from chain_compiler.model.operator import OPERATORS

def convert_to_postfix(tokens):
    output = []
    op_stack = []
    
    for token in tokens:
        if token.type in ['CHAR', 'CHAR_CLASS']:
            output.append(token)
        elif token.type in ['OPERATOR', 'QUANTIFIER']:
            current_op = OPERATORS.get(token.value)
            if not current_op:
                raise ValueError(f"Operador desconocido: {token.value}")
            while op_stack:
                top = op_stack[-1]
                if top.type in ['OPERATOR', 'QUANTIFIER']:
                    top_op = OPERATORS.get(top.value)
                    if top_op and ((current_op.associativity == 'left' and current_op.precedence <= top_op.precedence) or
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
            while op_stack and op_stack[-1].type != 'LPAREN':
                output.append(op_stack.pop())
            if op_stack and op_stack[-1].type == 'LPAREN':
                op_stack.pop()
            else:
                raise ValueError("Paréntesis desbalanceados")
    
    while op_stack:
        top = op_stack.pop()
        if top.type in ['LPAREN', 'RPAREN']:
            raise ValueError("Paréntesis desbalanceados")
        output.append(top)
    
    return output