"""
Módulo para la optimización de DFA.
Implementa el algoritmo de Hopcroft para minimizar un DFA.
"""

from afd_compiler.models.dfa import DFA

def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimiza un DFA usando Hopcroft y preserva el mapa state_tokens.
    """
    # 1) Partición inicial: separamos no-aceptantes y, entre los aceptantes,
    #    un bloque POR CADA token distinto.
    Q     = set(dfa.states)
    F     = set(dfa.accepting_states)
    nonF  = Q - F

    # Bloque de no-aceptantes
    P = []
    if nonF:
        P.append(nonF)

    # Bloques de aceptantes, uno para cada token
    token_to_states = {}
    for s in F:
        tok = dfa.state_tokens[s]
        token_to_states.setdefault(tok, set()).add(s)
    P.extend(token_to_states.values())

    # La “work list” arranca con todos esos bloques
    W = list(P)

    # 2) Refinar la partición
    while W:
        A = W.pop(0)
        for c in dfa.alphabet:
            new_P = []
            for Y in P:
                # X = estados en Y que con 'c' van a A
                X = {
                    s for s in Y
                    if (s, c) in dfa.transitions
                       and dfa.transitions[(s, c)] in A
                }
                if X and X != Y:
                    Y_minus_X = Y - X
                    new_P.extend([X, Y_minus_X])
                    # mantener W consistente
                    if Y in W:
                        W.remove(Y)
                        W.extend([X, Y_minus_X])
                    else:
                        # añadir sólo el bloque más pequeño
                        W.append(X if len(X) <= len(Y_minus_X) else Y_minus_X)
                else:
                    new_P.append(Y)
            P = new_P

    # 3) Construir mapping de estados viejos → nuevos bloques
    state_mapping = {}
    new_states    = set()
    for block in P:
        block_frozen = frozenset(block)
        new_states.add(block_frozen)
        for s in block:
            state_mapping[s] = block_frozen

    # 4) Reconstruir transiciones con los bloques
    new_transitions = {}
    for (src, sym), dst in dfa.transitions.items():
        new_transitions[(state_mapping[src], sym)] = state_mapping[dst]

    # 5) Nuevo estado inicial y nuevos estados de aceptación
    new_initial   = state_mapping[dfa.initial_state]
    new_accepting = { state_mapping[s] for s in dfa.accepting_states }

    # **6) PRESERVAR state_tokens**: 
    #     por cada estado viejo que tenía token, asignarlo al bloque nuevo
    new_state_tokens = {}
    for old_state, tok in dfa.state_tokens.items():
        new_block = state_mapping[old_state]
        new_state_tokens[new_block] = tok

    # 7) Devolver el nuevo DFA con su state_tokens
    return DFA(
        new_states,
        dfa.alphabet,
        new_transitions,
        new_initial,
        new_accepting,
        new_state_tokens
    )


def visualize_minimized_dfa(dfa: DFA, filename: str = 'minimized_dfa'):
    minimized = minimize_dfa(dfa)
    return minimized.visualize(filename)
