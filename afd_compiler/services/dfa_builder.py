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
    """Construye un AFD utilizando el método directo a partir del AST."""
    Position.reset_counter()
    
    end_marker = ASTNode('CHAR', '#', [])
    new_root = ASTNode('OPERATOR', '&', [ast, end_marker])
    
    for node in traverse_tree(new_root):
        node.nullable = False
        node.firstpos = set()
        node.lastpos = set()
    
    calculate_node_functions(new_root)
    followpos = calculate_followpos(new_root)
    alphabet = get_alphabet(new_root)
    initial_state = frozenset(new_root.firstpos)
    
    states = {initial_state}
    unmarked_states = {initial_state}
    transitions = {}
    accepting_states = set()
    
    end_position = next(pos for pos in new_root.lastpos if pos.symbol == '#')
    
    while unmarked_states:
        current_state = unmarked_states.pop()
        
        if end_position in current_state:
            accepting_states.add(current_state)
        
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
    
    return DFA(states, alphabet, transitions, initial_state, accepting_states)
