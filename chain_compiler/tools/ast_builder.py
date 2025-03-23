import copy
from chain_compiler.model.ast_node import ASTNode
from chain_compiler.model.operator import OPERATORS
from string import printable

def expand_char_class(token):
    """
    Expande una clase de caracteres en un AST de unión.
    Soporta clases normales y clases negadas ([^...]).

    Args:
        token (Token): Token con valor "[a-z]" o "[^abc]"

    Returns:
        ASTNode: AST que representa la unión (|) de todos los caracteres permitidos
    """
    content = token.value[1:-1]
    is_negated = content.startswith('^')
    if is_negated:
        content = content[1:]

    char_set = set()
    i = 0
    while i < len(content):
        if i + 2 < len(content) and content[i+1] == '-':
            start = content[i]
            end = content[i+2]
            for c in range(ord(start), ord(end)+1):
                char_set.add(chr(c))
            i += 3
        else:
            char_set.add(content[i])
            i += 1

    if not char_set:
        raise ValueError("Clase de caracteres vacía")

    if is_negated:
        all_chars = set(printable) 
        char_set = all_chars - char_set

    # Convertimos el set final a AST de unión
    sorted_chars = sorted(char_set)
    union_ast = ASTNode('CHAR', sorted_chars[0])
    for ch in sorted_chars[1:]:
        union_ast = ASTNode('OPERATOR', '|', [union_ast, ASTNode('CHAR', ch)])

    return union_ast

def build_ast(postfix_tokens):
    stack = []
    for token in postfix_tokens:
        if token.type == 'CHAR':
            node = ASTNode('CHAR', token.value)
            stack.append(node)
        elif token.type == 'CHAR_CLASS':
            node = expand_char_class(token)
            stack.append(node)
        elif token.type in ['OPERATOR', 'QUANTIFIER']:
            op = token.value
            operator = OPERATORS.get(op)
            if not operator:
                raise ValueError(f"Operador desconocido: {op}")
            if operator.arity == 1:
                if len(stack) < 1:
                    raise ValueError("Insuficientes operandos para el operador " + op)
                child = stack.pop()
                if op == '+':
                    node = ASTNode('OPERATOR', '&', [
                        child,
                        ASTNode('OPERATOR', '*', [copy.deepcopy(child)])
                    ])
                else:
                    node = ASTNode('OPERATOR', op, [child])
                stack.append(node)
            elif operator.arity == 2:
                if len(stack) < 2:
                    raise ValueError("Insuficientes operandos para el operador " + op)
                right = stack.pop()
                left = stack.pop()
                node = ASTNode('OPERATOR', op, [left, right])
                stack.append(node)
    if len(stack) != 1:
        raise ValueError("Expresión inválida, no se pudo construir un AST único.")
    return stack[0]
