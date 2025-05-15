# YAPar/grammar_ast.py

from typing import List, NamedTuple

class Production(NamedTuple):
    lhs: str
    rhs: List[List[str]]

class Grammar:
    def __init__(self,
                 tokens: List[str],
                 ignore: List[str],
                 productions: List[Production]):
        self.tokens = tokens
        self.ignore = ignore
        self.productions = productions

        # — Atributos extra para FIRST/FOLLOW tests —
        self.start_symbol = productions[0].lhs if productions else None
        self.terminals    = [t for t in tokens if t not in ignore]
        self.eof_token    = '$'
        # ——————————————————————————————

    def __repr__(self):
        lines = ["Grammar:",
                 f"  Tokens: {self.tokens}",
                 f"  Ignore: {self.ignore}",
                 "  Productions:"]
        for p in self.productions:
            rhss = [" ".join(rhs) for rhs in p.rhs]
            lines.append(f"    {p.lhs} -> {' | '.join(rhss)}")
        return "\n".join(lines)
