from ..models.position import Position

def traverse_tree(node):
    """Generador que recorre el árbol en pre-orden."""
    yield node
    for child in node.children:
        yield from traverse_tree(child)

def calculate_node_functions(node):
    """Calcula nullable, firstpos y lastpos para cada nodo del árbol."""
    if node.type == 'CHAR' or node.type == 'CHAR_CLASS':
        pos = Position(node.value)
        node.nullable = False
        node.firstpos = {pos}
        node.lastpos = {pos}
    
    elif node.type == 'OPERATOR':
        if node.value == '|':
            left, right = node.children
            calculate_node_functions(left)
            calculate_node_functions(right)
            
            node.nullable = left.nullable or right.nullable
            node.firstpos = left.firstpos | right.firstpos
            node.lastpos = left.lastpos | right.lastpos
            
        elif node.value == '&':
            left, right = node.children
            calculate_node_functions(left)
            calculate_node_functions(right)
            
            node.nullable = left.nullable and right.nullable
            node.firstpos = left.firstpos | (right.firstpos if left.nullable else set())
            node.lastpos = right.lastpos | (left.lastpos if right.nullable else set())
            
        elif node.value in ['*', '?']:
            child = node.children[0]
            calculate_node_functions(child)
            
            node.nullable = True
            node.firstpos = child.firstpos
            node.lastpos = child.lastpos
            
        elif node.value == '+':
            child = node.children[0]
            calculate_node_functions(child)
            
            node.nullable = False
            node.firstpos = child.firstpos
            node.lastpos = child.lastpos

def calculate_followpos(node, followpos=None):
    """Calcula followpos para todo el árbol."""
    if followpos is None:
        followpos = {}
    
    if node.type == 'OPERATOR':
        if node.value == '&':
            left, right = node.children
            for pos in left.lastpos:
                if pos not in followpos:
                    followpos[pos] = set()
                followpos[pos].update(right.firstpos)
        
        elif node.value in ['*', '+']:
            for pos in node.lastpos:
                if pos not in followpos:
                    followpos[pos] = set()
                followpos[pos].update(node.firstpos)
        
        for child in node.children:
            calculate_followpos(child, followpos)
    
    return followpos

def expand_char_class(class_str):
    """
    Expande una clase de caracteres del formato [a-z] o similar en un conjunto de caracteres.
    Soporta rangos y caracteres individuales.
    """
    content = class_str[1:-1]  # Remueve los corchetes
    chars = set()
    i = 0
    while i < len(content):
        if i + 2 < len(content) and content[i+1] == '-':
            start = content[i]
            end = content[i+2]
            for c in range(ord(start), ord(end) + 1):
                chars.add(chr(c))
            i += 3
        else:
            chars.add(content[i])
            i += 1
    return chars

def get_alphabet(node, alphabet=None):
    """
    Obtiene el alfabeto de la expresión regular, incluyendo nodos de tipo CHAR y CHAR_CLASS.
    """
    if alphabet is None:
        alphabet = set()
    
    if node.type == 'CHAR' and node.value != '#':
        alphabet.add(node.value)
    elif node.type == 'CHAR_CLASS':
        expanded = expand_char_class(node.value)
        alphabet.update(expanded)
    
    for child in node.children:
        get_alphabet(child, alphabet)
    
    return alphabet
