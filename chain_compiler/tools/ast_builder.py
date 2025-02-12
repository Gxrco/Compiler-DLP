from chain_compiler.model.ast_node import ASTNode
from chain_compiler.model.operator import OPERATORS

def build_ast(postfix_tokens):
    """
    Construye el Árbol de Sintaxis Abstracta (AST) a partir de la lista de tokens en notación postfix.

    Args:
        postfix_tokens (list): Lista de tokens en notación postfix.

    Returns:
        ASTNode: Nodo raíz del AST.
    """
    stack = []
    for token in postfix_tokens:
        if token.type in ['CHAR', 'CHAR_CLASS']:
            node = ASTNode('CHAR', token.value)
            stack.append(node)
        elif token.type in ['OPERATOR', 'QUANTIFIER']:
            if token.type == 'QUANTIFIER':
                operator = OPERATORS['QUANTIFIER']
            else:
                if token.value not in OPERATORS:
                    raise ValueError(f"Operador desconocido: {token.value}")
                operator = OPERATORS[token.value]
            if operator.arity == 1:
                if len(stack) < 1:
                    raise ValueError("Insuficientes operandos para el operador " + token.value)
                child = stack.pop()
                node = ASTNode('OPERATOR', token.value, [child])
                stack.append(node)
            elif operator.arity == 2:
                if len(stack) < 2:
                    raise ValueError("Insuficientes operandos para el operador " + token.value)
                right = stack.pop()
                left = stack.pop()
                node = ASTNode('OPERATOR', token.value, [left, right])
                stack.append(node)
    if len(stack) != 1:
        raise ValueError("Expresión inválida, no se pudo construir un AST único.")
    return stack[0]
