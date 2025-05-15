# YAPar/slr_table_generator.py

from typing import Dict, Tuple, List, Set
from YAPar.model.item import Item
from YAPar.lr0_builder import build_lr0_states
from YAPar.utils.first_follow import compute_first, compute_follow
from YAPar.utils.closure_goto import goto
from YAPar.grammar_parser import parse_file

def build_slr_parsing_table(
    grammar_path: str
) -> Tuple[
    List[Set[Item]],                        # estados LR(0)
    Dict[Tuple[int, str], Tuple[str, int]], # action table: (state,symbol)->(action, target)
    Dict[Tuple[int, str], int]              # goto table: (state, nonterm)->state
]:
    """
    Lee la gramática en grammar_path, construye:
      - colección canónica de estados LR(0),
      - tabla ACTION para shift/reduce/accept,
      - tabla GOTO para no-terminales.
    """
    # 1) Parsear gramática
    grammar = parse_file(grammar_path)
    prods   = [(p.lhs, p.rhs) for p in grammar.productions]

    # 2) Augmentar con S' -> S
    start       = grammar.start_symbol
    start_prime = start + "'"
    aug_prods   = [(start_prime, [[start]])] + prods

    # 3) Construir estados LR(0)
    states = build_lr0_states(aug_prods, start_prime)

    # 4) FIRST y FOLLOW sobre la gramática original
    first_sets  = compute_first(grammar)
    follow_sets = compute_follow(grammar, first_sets)

    # 5) Derivar terminales de las producciones augmentadas
    nonterms = {lhs for (lhs, _) in aug_prods}
    symbols  = set()
    for _, rhss in aug_prods:
        for rhs in rhss:
            symbols.update(rhs)
    terminals = [s for s in symbols if s not in nonterms]
    EOF       = grammar.eof_token

    # 6) Inicializar tablas
    action:   Dict[Tuple[int, str], Tuple[str, int]] = {}
    goto_tbl: Dict[Tuple[int, str], int]          = {}

    # 7) Rellenar ACTION
    for i, I in enumerate(states):
        for it in I:
            # shift
            if it.dot < len(it.rhs):
                a = it.rhs[it.dot]
                if a in terminals:
                    J = goto(I, a, aug_prods)
                    j = states.index(J)
                    action[(i, a)] = ('shift', j)

            # reduce o accept
            if it.dot == len(it.rhs):
                if it.lhs == start_prime:
                    action[(i, EOF)] = ('accept', None)
                else:
                    # buscar índice de producción A→rhs
                    prod_index = None
                    for idx2, (lhs2, rhss2) in enumerate(prods):
                        if lhs2 == it.lhs and it.rhs in rhss2:
                            prod_index = idx2
                            break
                    if prod_index is None:
                        raise ValueError(f"No encuentro producción para {it}")
                    for b in follow_sets[it.lhs]:
                        action[(i, b)] = ('reduce', prod_index)

    # 8) Rellenar GOTO
    nonterms2 = {lhs for (lhs, _) in prods}
    for i, I in enumerate(states):
        for A in nonterms2:
            J = goto(I, A, aug_prods)
            if J:
                j = states.index(J)
                goto_tbl[(i, A)] = j

    return states, action, goto_tbl
