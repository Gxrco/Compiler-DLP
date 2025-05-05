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
        """Genera una visualización del AFD usando Graphviz con manejo mejorado de caracteres especiales."""
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
                token_label = self._escape_label(self.state_tokens[state])
                label = f"{name}\\n{token_label}"
                
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
        
        # Agregar aristas para las transiciones con manejo especial de caracteres
        for (src_name, dst_name), symbols in grouped_transitions.items():
            # Sanitizar y escapar caracteres especiales en los símbolos
            safe_symbols = [self._escape_symbol(s) for s in symbols]
            edge_label = ','.join(sorted(safe_symbols))
            dot.edge(src_name, dst_name, edge_label)
        
        # Renderizar solo si el archivo no es muy largo (para evitar problemas con nombres largos)
        safe_filename = self._safe_filename(filename)
        try:
            dot.render(safe_filename, view=True, format='pdf', cleanup=True)
        except Exception as e:
            print(f"Error al renderizar el DFA: {e}")
            # Intentar con un nombre más corto si falla
            try:
                dot.render('dfa_graph', view=True, format='pdf', cleanup=True)
            except Exception as e2:
                print(f"No se pudo renderizar el DFA: {e2}")
        
        return dot
    
    def _escape_symbol(self, symbol):
        """Escapa caracteres especiales para que sean seguros en Graphviz."""
        # Mapa de caracteres especiales y sus versiones escapadas
        special_chars = {
            '\\': '\\\\',  # Backslash
            '{': '\\{',    # Llaves
            '}': '\\}',
            '"': '\\"',    # Comillas
            "'": "\\'",
            '<': '\\<',    # Otros caracteres especiales
            '>': '\\>',
            '|': '\\|',
            '&': '\\&',
            '^': '\\^',
            '$': '\\$',
            '#': '\\#',
            '=': '\\='
        }
        
        # Si es un carácter especial, usar su versión escapada
        if symbol in special_chars:
            return special_chars[symbol]
        
        # Para otros caracteres no imprimibles o espacios, usar su representación
        if symbol in ' \t\n\r':
            if symbol == ' ':
                return 'SP'
            elif symbol == '\t':
                return '\\t'
            elif symbol == '\n':
                return '\\n'
            elif symbol == '\r':
                return '\\r'
        
        return symbol
    
    def _escape_label(self, label):
        """Escapa etiquetas completas para Graphviz."""
        # Reemplazar caracteres que podrían causar problemas en etiquetas
        if isinstance(label, str):
            for char, replacement in [
                ('\\', '\\\\'), 
                ('"', '\\"'), 
                ('{', '\\{'), 
                ('}', '\\}'),
                ('<', '\\<'),
                ('>', '\\>'),
                ('|', '\\|'),
                ('=', '\\=')
            ]:
                label = label.replace(char, replacement)
        return label
    
    def _safe_filename(self, filename):
        """Crea un nombre de archivo seguro, limitando su longitud y caracteres especiales."""
        # Reemplazar caracteres no alfanuméricos por guiones bajos
        import re
        safe_name = re.sub(r'[^\w]', '_', filename)
        
        # Limitar la longitud del nombre del archivo
        if len(safe_name) > 50:
            safe_name = safe_name[:45] + '_dfa'
            
        return safe_name