# YAPar/grammar_ast.py

from typing import List, NamedTuple

class Production(NamedTuple):
    lhs: str
    rhs: List[List[str]]  # cada RHS es una lista de símbolos (tokens o no-terminales)

class Grammar:
    """
    Representa una gramática YAPar completamente parseada.
    - tokens: lista de nombres de token (terminales)
    - ignore: lista de tokens a ignorar
    - productions: lista de Production
    """
    def __init__(self,
                 tokens: List[str],
                 ignore: List[str],
                 productions: List[Production]):
        self.tokens = tokens
        self.ignore = ignore
        self.productions = productions

    def __repr__(self):
        lines = ["Grammar:",
                 f"  Tokens: {self.tokens}",
                 f"  Ignore: {self.ignore}",
                 "  Productions:"]
        for p in self.productions:
            rhss = [" ".join(rhs) for rhs in p.rhs]
            lines.append(f"    {p.lhs} -> {' | '.join(rhss)}")
        return "\n".join(lines)
