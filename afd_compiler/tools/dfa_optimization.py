"""
Módulo para la optimización de DFA.
Implementa el algoritmo de Hopcroft para minimizar un DFA.
"""

from afd_compiler.models.dfa import DFA

def minimize_dfa(dfa: DFA) -> DFA:
    Q = set(dfa.states)
    F = set(dfa.accepting_states)
    nonF = Q - F
    P = []
    if F:
        P.append(F)
    if nonF:
        P.append(nonF)

    W = list(P)

    while W:
        A = W.pop(0)  
        for c in dfa.alphabet:
            new_P = []
            for Y in P:
                X = { s for s in Y if (s, c) in dfa.transitions and dfa.transitions[(s, c)] in A }
                if X and X != Y:
                    new_P.append(X)
                    new_P.append(Y - X)

                    if Y in W:
                        W.remove(Y)
                        W.append(X)
                        W.append(Y - X)
                    else:

                        if len(X) <= len(Y - X):
                            W.append(X)
                        else:
                            W.append(Y - X)
                else:
                    new_P.append(Y)
            P = new_P

    state_mapping = {}
    new_states = set()
    for block in P:
        block_frozen = frozenset(block)  
        new_states.add(block_frozen)
        for s in block:
            state_mapping[s] = block_frozen

    
    new_transitions = {}
    for block in new_states: 
        rep = next(iter(block))
        for c in dfa.alphabet:
            if (rep, c) in dfa.transitions:
                target = dfa.transitions[(rep, c)]
                new_transitions[(block, c)] = state_mapping[target]

   
    new_initial = state_mapping[dfa.initial_state]
    new_accepting = { state_mapping[s] for s in dfa.accepting_states }

    return DFA(new_states, dfa.alphabet, new_transitions, new_initial, new_accepting)



def visualize_minimized_dfa(dfa: DFA, filename: str = 'minimized_dfa'):
    minimized = minimize_dfa(dfa)
    return minimized.visualize(filename)
