from collections import defaultdict

def compute_first(grammar):
    """
    Devuelve un dict: símbolo → conjunto FIRST(símbolo).
    Usamos '' para ε.
    """
    # Terminales reales = tokens menos los que se ignoran
    terminals = set(grammar.tokens) - set(grammar.ignore)
    # No–terminales = todos los lhs de producciones
    nonterms = {prod.lhs for prod in grammar.productions}

    FIRST = {A: set() for A in nonterms}
    # Inicializa FIRST de terminales
    for t in terminals:
        FIRST[t] = {t}

    EPS = ''

    changed = True
    while changed:
        changed = False
        for prod in grammar.productions:
            A = prod.lhs
            for rhs in prod.rhs:
                # ε-producción
                if not rhs:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
                    continue

                nullable = True
                for X in rhs:
                    # A <- X ... Añade FIRST(X)\{ε} a FIRST(A)
                    to_add = FIRST.get(X, set()) - {EPS}
                    if to_add - FIRST[A]:
                        FIRST[A].update(to_add)
                        changed = True
                    # Si X no genera ε, paramos aquí
                    if EPS not in FIRST.get(X, set()):
                        nullable = False
                        break
                if nullable and EPS not in FIRST[A]:
                    FIRST[A].add(EPS)
                    changed = True

    return FIRST


def compute_follow(grammar, FIRST):
    """
    Devuelve un dict: no-terminal → conjunto FOLLOW(no-terminal).
    Usa grammar.eof_token como EOF.
    """
    nonterms = {prod.lhs for prod in grammar.productions}
    FOLLOW = {A: set() for A in nonterms}
    EOF = grammar.eof_token
    FOLLOW[grammar.start_symbol].add(EOF)

    EPS = ''

    changed = True
    while changed:
        changed = False
        for prod in grammar.productions:
            A = prod.lhs
            for rhs in prod.rhs:
                trailer = FOLLOW[A].copy()
                # Recorre de derecha a izquierda
                for X in reversed(rhs):
                    if X in nonterms:
                        if trailer - FOLLOW[X]:
                            FOLLOW[X].update(trailer)
                            changed = True
                        # Si FIRST(X) tiene ε, trailer += FIRST(X)\{ε}
                        if EPS in FIRST.get(X, set()):
                            trailer = trailer.union(FIRST[X] - {EPS})
                        else:
                            trailer = FIRST[X].copy()
                    else:
                        # X es terminal → trailer = {X}
                        trailer = {X}

    return FOLLOW
