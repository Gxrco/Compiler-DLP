from afd_compiler.services.dfa_builder import build_direct_dfa 
from afd_compiler.tools.dfa_optimization import minimize_dfa

class AFDService:
    """
    Servicio que encapsula el proceso de construcción, optimización y uso del AFD.
    """
    def __init__(self):
        self.dfa = None
    
    def build_dfa_from_ast(self, ast):
        """
        Construye un AFD a partir de un AST.
        """
        self.dfa = build_direct_dfa(ast)
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
