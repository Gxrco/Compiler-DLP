from afd_compiler.services.dfa_builder import build_direct_dfa 
from afd_compiler.tools.dfa_optimization import minimize_dfa

class AFDService:
    """
    Servicio que encapsula el proceso de construcción, optimización y uso del AFD.
    """
    def __init__(self):
        self.dfa = None
    
    def build_dfa_from_ast(self, ast, already_marked=False):
        from afd_compiler.services.dfa_builder import build_direct_dfa
        self.dfa = build_direct_dfa(ast, already_marked)
        return self.dfa

    def minimize_dfa(self):
        """
        Minimiza el DFA previamente construido y actualiza el atributo dfa.
        """
        if self.dfa is None:
            raise ValueError("DFA no ha sido construido")
        self.dfa = minimize_dfa(self.dfa)
        return self.dfa
    
    def match(self, string):
        """
        Verifica si una cadena es aceptada por el AFD.
        """
        if self.dfa is None:
            raise ValueError("DFA no ha sido construido")
        return self.dfa.accepts(string)
    
    def get_dfa_info(self):
        """
        Retorna información sobre el AFD construido.
        """
        if self.dfa is None:
            raise ValueError("DFA no ha sido construido")
        
        return {
            "states_count": len(self.dfa.states),
            "alphabet": sorted(list(self.dfa.alphabet)),
            "transitions_count": len(self.dfa.transitions),
            "accepting_states_count": len(self.dfa.accepting_states)
        }
    def scan_input(self, input_str):
        """
        ETAPA 4 – Reconocimiento y simbolización:
        Escanea una cadena de entrada utilizando el DFA para extraer tokens junto con su lexema.
        
        Args:
            input_str (str): Cadena de entrada a analizar.
        
        Returns:
            list of tuple: Lista de tuplas (token_type, lexeme).
        """
        tokens = []
        index = 0
        while index < len(input_str):
            current_state = self.dfa.initial_state
            last_accepting_index = -1
            last_accepting_token = None
            i = index
            while i < len(input_str):
                char = input_str[i]
                if char not in self.dfa.alphabet:
                    break
                key = (current_state, char)
                if key not in self.dfa.transitions:
                    break
                current_state = self.dfa.transitions[key]
                if current_state in self.dfa.accepting_states:
                    last_accepting_index = i
                    last_accepting_token = self.dfa.state_tokens.get(current_state, "ACCEPT")
                i += 1
            if last_accepting_index >= index:
                lexeme = input_str[index:last_accepting_index+1]
                tokens.append((last_accepting_token, lexeme))
                index = last_accepting_index + 1
            else:
                tokens.append(("ERROR", input_str[index]))
                index += 1
        return tokens


