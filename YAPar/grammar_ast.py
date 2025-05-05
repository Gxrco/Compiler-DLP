# YAPar/grammar_ast.py

from typing import List

class Production:
    def __init__(self, lhs: str, rhs_alts: List[List[str]]):
        """
        lhs: nombre no-terminal de la producción, e.g. "expression"
        rhs_alts: lista de alternativas, cada una es lista de símbolos
                  e.g. [["expression","PLUS","term"], ["term"]]
        """
        self.lhs = lhs
        self.rhs_alts = rhs_alts

    def __repr__(self):
        alts = [" ".join(alt) for alt in self.rhs_alts]
        return f"{self.lhs} → {' | '.join(alts)}"

class Grammar:
    def __init__(self,
                 tokens: List[str],
                 ignore:  List[str],
                 productions: List[Production]):
        """
        tokens: lista de nombres de token declarados (%token)
        ignore: lista de tokens a ignorar (IGNORE)
        productions: lista de Production
        """
        self.tokens = tokens
        self.ignore = ignore
        self.productions = productions

    def __repr__(self):
        lines = ["Tokens: " + ", ".join(self.tokens),
                 "Ignore: " + ", ".join(self.ignore),
                 "Productions:"]
        lines += [f"  {p!r}" for p in self.productions]
        return "\n".join(lines)
