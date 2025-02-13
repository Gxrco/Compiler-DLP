from graphviz import Digraph

class DFA:
    """Clase que representa un Autómata Finito Determinista (AFD)."""
    def __init__(self, states, alphabet, transitions, initial_state, accepting_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        
    def accepts(self, string):
        """Verifica si la cadena es aceptada por el AFD."""
        current = self.initial_state
        for symbol in string:
            if symbol not in self.alphabet:
                return False
            if (current, symbol) not in self.transitions:
                return False
            current = self.transitions[(current, symbol)]
        return current in self.accepting_states
    
    def visualize(self, filename='dfa_graph'):
        """Genera una visualización del AFD usando Graphviz."""
        dot = Digraph()
        dot.attr(rankdir='LR')
        
        dot.node('', '', shape='none')
        
        state_names = {state: f'q{i}' for i, state in enumerate(self.states)}
        
        for state in self.states:
            name = state_names[state]
            shape = 'doublecircle' if state in self.accepting_states else 'circle'
            dot.node(name, name, shape=shape)
        
        dot.edge('', state_names[self.initial_state])
        
        grouped_transitions = {}
        for (src_state, symbol), dst_state in self.transitions.items():
            key = (state_names[src_state], state_names[dst_state])
            if key not in grouped_transitions:
                grouped_transitions[key] = []
            grouped_transitions[key].append(symbol)
        
        for (src_name, dst_name), symbols in grouped_transitions.items():
            dot.edge(src_name, dst_name, ','.join(sorted(symbols)))
        
        dot.render(filename, view=True, format='pdf', cleanup=True)
        return dot
