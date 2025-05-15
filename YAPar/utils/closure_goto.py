# YAPar/utils/closure_goto.py

from typing import Set
from YAPar.model.item import Item

def closure(items: Set[Item], productions) -> Set[Item]:
    """
    Dado un conjunto inicial de ítems LR(0), devuelve su cierre:
    si hay A → α • B β en items, añade B → • γ para cada alternativa γ de B.
    productions es una lista de tuplas (lhs, [rhs1, rhs2, ...]),
    donde cada rhsi es una lista de símbolos.
    """
    closure_set = set(items)
    added = True
    while added:
        added = False
        for it in list(closure_set):
            # Si el punto no está al final
            if it.dot < len(it.rhs):
                B = it.rhs[it.dot]
                # Por cada producción cuya izquierda sea B
                for lhs, rhss in productions:
                    if lhs == B:
                        for gamma in rhss:
                            new_it = Item(lhs=lhs, rhs=gamma, dot=0)
                            if new_it not in closure_set:
                                closure_set.add(new_it)
                                added = True
    return closure_set

def goto(items: Set[Item], symbol: str, productions) -> Set[Item]:
    """
    GOTO(items, symbol): desplaza • sobre symbol y cierra el conjunto resultante.
    """
    moved = set()
    for it in items:
        if it.dot < len(it.rhs) and it.rhs[it.dot] == symbol:
            moved_it = Item(lhs=it.lhs, rhs=it.rhs, dot=it.dot + 1)
            moved.add(moved_it)
    return closure(moved, productions)
