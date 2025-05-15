# YAPar/lr0_builder.py

from typing import List, Set, Tuple
from YAPar.model.item import Item
from YAPar.utils.closure_goto import closure, goto

def build_lr0_states(
    productions: List[Tuple[str, List[List[str]]]],
    start_symbol: str
) -> List[Set[Item]]:
    """
    Construye la colección canónica C de conjuntos de ítems LR(0):
      1. Estado 0 = closure({S'→•α}), donde α es la RHS de la producción augmentada.
      2. Para cada estado I en C y cada símbolo X en la gramática:
           si GOTO(I, X) ≠ ∅ y aún no está en C, añadirlo a C.
    Retorna la lista de estados (cada uno es un Set[Item]).
    """
    # 1) Ítem inicial a partir de la primera producción (la augmentada)
    #    productions[0] debe ser (start_symbol, [[original_start]])
    augment_lhs, augment_rhss = productions[0]
    # Tomamos la primera alternativa de RHS
    initial_rhs = augment_rhss[0]
    I0 = closure({ Item(lhs=augment_lhs, rhs=initial_rhs, dot=0) }, productions)

    states: List[Set[Item]] = [I0]
    # Recopilar todos los símbolos (terminales y no-terminales)
    symbols = set()
    for lhs, rhss in productions:
        symbols.add(lhs)
        for rhs in rhss:
            symbols.update(rhs)

    # 2) Construir la colección canónica
    idx = 0
    while idx < len(states):
        I = states[idx]
        for X in symbols:
            J = goto(I, X, productions)
            if J and J not in states:
                states.append(J)
        idx += 1

    return states
