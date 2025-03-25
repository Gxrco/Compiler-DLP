from graphviz import Digraph

class DFA:
    """Clase que representa un Autómata Finito Determinista (AFD)."""
    def __init__(self, states, alphabet, transitions, initial_state, accepting_states, state_tokens=None):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        self.state_tokens = state_tokens or {}  # Mapeo de estados a tokens
        
    def accepts(self, string):
        """
        Verifica si la cadena es aceptada por el AFD.
        Retorna el token correspondiente si es aceptada, None en caso contrario.
        """
        current = self.initial_state
        for symbol in string:
            if symbol not in self.alphabet:
                return None
            if (current, symbol) not in self.transitions:
                return None
            current = self.transitions[(current, symbol)]
        
        if current in self.accepting_states:
            token = self.state_tokens.get(current, "ACCEPT")
            return token
        return None
    
    def visualize(self, filename='dfa_graph'):
        """Genera una visualización del AFD usando Graphviz."""
        dot = Digraph()
        dot.attr(rankdir='LR')
        
        dot.node('', '', shape='none')
        
        # Generar nombres más legibles para los estados
        state_names = {state: f'q{i}' for i, state in enumerate(self.states)}
        
        # Crear nodos para cada estado
        for state in self.states:
            name = state_names[state]
            shape = 'doublecircle' if state in self.accepting_states else 'circle'
            
            # Añadir etiqueta de token si es un estado de aceptación
            label = name
            if state in self.accepting_states and state in self.state_tokens:
                label = f"{name}\\n{self.state_tokens[state]}"
                
            dot.node(name, label, shape=shape)
        
        # Agregar arista desde el inicio al estado inicial
        dot.edge('', state_names[self.initial_state])
        
        # Agrupar transiciones para mejor legibilidad
        grouped_transitions = {}
        for (src_state, symbol), dst_state in self.transitions.items():
            key = (state_names[src_state], state_names[dst_state])
            if key not in grouped_transitions:
                grouped_transitions[key] = []
            grouped_transitions[key].append(symbol)
        
        # Agregar aristas para las transiciones
        for (src_name, dst_name), symbols in grouped_transitions.items():
            dot.edge(src_name, dst_name, ','.join(sorted(symbols)))
        
        # Renderizar el gráfico
        dot.render(filename, view=True, format='pdf', cleanup=True)
        return dot