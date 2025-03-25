from chain_compiler.model.ast_node import ASTNode
from ..models.position import Position
from ..models.dfa import DFA
from ..utils.ast_functions import (
    traverse_tree, 
    calculate_node_functions, 
    calculate_followpos, 
    get_alphabet
)

def build_direct_dfa(ast):
    """
    Construye un AFD utilizando el método directo a partir del AST.
    Preserva la información de token para cada estado de aceptación.
    """
    Position.reset_counter()
    
    # Modificar el árbol para incluir un marcador de final de patrón
    end_marker = ASTNode('CHAR', '#', [])
    new_root = ASTNode('OPERATOR', '&', [ast, end_marker])
    
    # Inicializar las funciones de nodos
    for node in traverse_tree(new_root):
        node.nullable = False
        node.firstpos = set()
        node.lastpos = set()
    
    # Calcular funciones de nodos y followpos
    calculate_node_functions(new_root)
    followpos = calculate_followpos(new_root)
    alphabet = get_alphabet(new_root)
    initial_state = frozenset(new_root.firstpos)
    
    # Construir el DFA
    states = {initial_state}
    unmarked_states = {initial_state}
    transitions = {}
    accepting_states = set()
    state_tokens = {}  # Mapeo de estados a tokens
    
    # Identificar la posición del marcador de final
    end_position = next(pos for pos in new_root.lastpos if pos.symbol == '#')
    
    # Implementar el algoritmo de construcción de DFA
    while unmarked_states:
        current_state = unmarked_states.pop()
        
        # Verificar si es un estado de aceptación
        if end_position in current_state:
            accepting_states.add(current_state)
            
            # Aquí podríamos añadir lógica para identificar el token asociado
            # Por ahora, simplemente usamos una etiqueta genérica
            state_tokens[current_state] = "TOKEN"
        
        # Calcular transiciones para cada símbolo del alfabeto
        for symbol in alphabet:
            next_state = set()
            for pos in current_state:
                if pos.symbol == symbol:
                    next_state.update(followpos.get(pos, set()))
            
            if next_state:
                next_state = frozenset(next_state)
                transitions[(current_state, symbol)] = next_state
                
                if next_state not in states:
                    states.add(next_state)
                    unmarked_states.add(next_state)
    
    # Crear y devolver el DFA
    dfa = DFA(states, alphabet, transitions, initial_state, accepting_states)
    
    # Añadir información de tokens (esto podría requerir modificar la clase DFA)
    # dfa.state_tokens = state_tokens
    
    return dfa