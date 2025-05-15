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
      1. Estado 0 = closure({S'→•α})
      2. Para cada estado I y cada símbolo X (no-terminal o terminal):
           si GOTO(I, X) ≠ ∅ y no está en C, añadirlo.
    Retorna la lista de estados (cada uno es un Set[Item]) en orden de descubrimiento.
    """
    # 1) Ítem inicial de la producción augmentada (siempre productions[0])
    aug_lhs, aug_rhss = productions[0]
    initial_rhs      = aug_rhss[0]
    I0 = closure({ Item(lhs=aug_lhs, rhs=initial_rhs, dot=0) }, productions)

    states: List[Set[Item]] = [I0]

    # 2) Determinar orden de símbolos: primero no-terminales (LHS en orden),
    #    luego terminales (aquellos símbolos que aparecen en RHS pero no son LHS),
    #    preservando su primer aparición.
    nonterms = [lhs for (lhs, _) in productions]

    seen = set()
    symbols_rhs = []
    for _, rhss in productions:
        for rhs in rhss:
            for sym in rhs:
                if sym not in seen:
                    seen.add(sym)
                    symbols_rhs.append(sym)

    terminals = [s for s in symbols_rhs if s not in nonterms]
    ordered_symbols = nonterms + terminals

    # 3) Generar la colección canónica
    idx = 0
    while idx < len(states):
        I = states[idx]
        for X in ordered_symbols:
            J = goto(I, X, productions)
            if J and J not in states:
                states.append(J)
        idx += 1

    return states
