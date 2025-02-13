import copy
from chain_compiler.model.ast_node import ASTNode
from chain_compiler.model.operator import OPERATORS

def expand_char_class(token):
    """
    Expande un token de tipo CHAR_CLASS en un AST que representa la unión (|) de
    todos los caracteres de la clase. Por ejemplo, "[A-Za-z]" se transforma en:
       (A|B|...|Z|a|b|...|z)
    
    Args:
        token (Token): Token de tipo CHAR_CLASS (con valor, por ejemplo, "[A-Za-z]")
    
    Returns:
        ASTNode: AST que representa la unión de cada carácter en la clase.
    
    Raises:
        NotImplementedError: Si la clase es negada (comienza con '^').
        ValueError: Si la clase está vacía.
    """
    # Se remueven los corchetes
    content = token.value[1:-1]
    if content and content[0] == '^':
        raise NotImplementedError("Clases negadas no implementadas")
    
    char_list = []
    i = 0
    while i < len(content):
        if i + 2 < len(content) and content[i+1] == '-':
            start = content[i]
            end = content[i+2]
            for code in range(ord(start), ord(end)+1):
                char_list.append(chr(code))
            i += 3
        else:
            char_list.append(content[i])
            i += 1
    if not char_list:
        raise ValueError("Clase de caracteres vacía")
    
    # Se crea el AST de unión: (char1 | char2 | ... | charN)
    union_ast = ASTNode('CHAR', char_list[0])
    for ch in char_list[1:]:
        new_node = ASTNode('CHAR', ch)
        union_ast = ASTNode('OPERATOR', '|', [union_ast, new_node])
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
