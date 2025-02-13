"""
Módulo para la optimización de DFA.
Implementa el algoritmo de particiones (refinamiento de particiones) para minimizar un DFA,
y además proporciona una función para graficar el DFA minimizado.
"""

from afd_compiler.models.dfa import DFA

def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimiza un DFA utilizando el algoritmo de particiones.

    Args:
        dfa (DFA): DFA original a minimizar.

    Returns:
        DFA: DFA minimizado.
    """
    accepting = set(dfa.accepting_states)
    non_accepting = set(dfa.states) - accepting

    P = []
    if accepting:
        P.append(accepting)
    if non_accepting:
        P.append(non_accepting)
    
    W = list(P) 

    while W:
        A = W.pop()
        for symbol in dfa.alphabet:
            X = { state for state in dfa.states 
                  if (state, symbol) in dfa.transitions and dfa.transitions[(state, symbol)] in A }
            
            new_P = []
            for Y in P:
                intersection = Y & X
                difference = Y - X
                if intersection and difference:
                    new_P.append(intersection)
                    new_P.append(difference)
                    
                    if Y in W:
                        W.remove(Y)
                        W.append(intersection)
                        W.append(difference)
                    else:
                        if len(intersection) <= len(difference):
                            W.append(intersection)
                        else:
                            W.append(difference)
                else:
                    new_P.append(Y)
            P = new_P

    new_states = set()
    state_map = {} 
    for block in P:
        new_state = frozenset(block)
        new_states.add(new_state)
        for s in block:
            state_map[s] = new_state

    new_transitions = {}
    for block in P:
        new_state = frozenset(block)
        representative = next(iter(block))
        for symbol in dfa.alphabet:
            if (representative, symbol) in dfa.transitions:
                target = dfa.transitions[(representative, symbol)]
                new_target = state_map[target]
                new_transitions[(new_state, symbol)] = new_target

    # Determinar el estado inicial y los de aceptación.
    new_initial = state_map[dfa.initial_state]
    new_accepting = { state_map[s] for s in dfa.accepting_states }

    return DFA(new_states, dfa.alphabet, new_transitions, new_initial, new_accepting)


def visualize_minimized_dfa(dfa: DFA, filename: str = 'minimized_dfa'):
    
    minimized_dfa = minimize_dfa(dfa)
    return minimized_dfa.visualize(filename)
