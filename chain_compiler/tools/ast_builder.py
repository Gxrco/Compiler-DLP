import copy
from chain_compiler.model.ast_node import ASTNode
from chain_compiler.model.operator import OPERATORS
from string import printable

def expand_char_class(token):
    content = token.value[1:-1]              # e.g. "^\\n" o "\\t0-9]"
    is_negated = content.startswith('^')
    if is_negated:
        content = content[1:]

    from string import printable
    char_set = set()
    i = 0
    while i < len(content):
        # 1) Si es una secuencia de escape \n, \t, \r, \\…
        if content[i] == '\\' and i+1 < len(content):
            esc = content[i+1]
            if esc == 'n':
                char_set.add('\n')
            elif esc == 't':
                char_set.add('\t')
            elif esc == 'r':
                char_set.add('\r')
            else:
                char_set.add(esc)
            i += 2

        # 2) Un rango a-b
        elif i+2 < len(content) and content[i+1] == '-':
            start, end = content[i], content[i+2]
            for c in range(ord(start), ord(end)+1):
                char_set.add(chr(c))
            i += 3

        # 3) Carácter suelto
        else:
            char_set.add(content[i])
            i += 1

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
    """
    Construye un AST a partir de tokens en notación postfix.
    
    Se hacen ajustes para manejar casos donde la expresión no está perfectamente formada.
    """
    stack = []
    
    # Filtrar tokens de marcadores especiales (TOKEN_MARKER)
    filtered_tokens = [token for token in postfix_tokens if token.type != 'TOKEN_MARKER']
    
    # Si hay un operador '|' al final sin operando derecho, lo removemos
    if filtered_tokens and filtered_tokens[-1].type == 'OPERATOR' and filtered_tokens[-1].value == '|':
        filtered_tokens.pop()
    
    for token in filtered_tokens:
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
            
            try:
                if operator.arity == 1:
                    if len(stack) < 1:
                        # Si no hay suficientes operandos, continuamos con el siguiente token
                        continue
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
                        # Si no hay suficientes operandos, continuamos con el siguiente token
                        continue
                    right = stack.pop()
                    left = stack.pop()
                    node = ASTNode('OPERATOR', op, [left, right])
                    stack.append(node)
            except Exception as e:
                print(f"Error procesando operador {op}: {e}")
                # Si ocurre un error, continuamos con el siguiente token
                continue
    
    # En caso de que la pila esté vacía, devolvemos un nodo vacío
    if not stack:
        return ASTNode('CHAR', 'ε')  # Epsilon representa la cadena vacía
    
    # Si hay más de un nodo en la pila, combinamos todo con operador |
    while len(stack) > 1:
        right = stack.pop()
        left = stack.pop()
        node = ASTNode('OPERATOR', '|', [left, right])
        stack.append(node)
    
    return stack[0]