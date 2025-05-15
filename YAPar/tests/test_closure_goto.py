import os
import unittest

from YAPar.grammar_parser  import parse_file
from YAPar.utils.closure_goto import closure, goto
from YAPar.model.item     import Item  # tu clase de ítem LR0

class ClosureGotoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Gramática de ejemplo
        here = os.path.dirname(__file__)
        demo   = os.path.normpath(os.path.join(here, "..", "examples", "demo.yalp"))
        cls.grammar = parse_file(demo)
        cls.prods   = cls.grammar.productions

        # ítem inicial "augmented start" por convención:
        # si start_symbol = S, creamos S' → • S
        cls.start_prime = cls.grammar.start_symbol + "'"
        cls.aug_prod    = [(cls.start_prime, [[cls.grammar.start_symbol]])] \
                          + [(p.lhs, p.rhs) for p in cls.prods]

        # construimos el primer ítem
        # Item toma (lhs, rhs_list, dot_pos)?
        cls.initial_item = Item(
            lhs=cls.start_prime,
            rhs=[cls.grammar.start_symbol],
            dot=0
        )

    def test_closure_adds_nonterminals(self):
        c = closure({self.initial_item}, self.aug_prod)
        # Debe contener el inicial...
        self.assertIn(self.initial_item, c)
        # ...y todos los ítems B→•γ cuando S'→•S y S→… aparece:
        # p.ej. expression → • expression PLUS term, term → • …
        # Comprobamos al menos que haya algún ítem cuyo lhs != start_prime
        others = [it for it in c if it.lhs != self.start_prime]
        self.assertTrue(len(others) >= 1)

    def test_goto_moves_dot(self):
        # Cierra el inicial
        c = closure({self.initial_item}, self.aug_prod)
        # GOTO sobre el símbolo original S
        g = goto(c, self.grammar.start_symbol, self.aug_prod)
        # Ahora debe existir el ítem S'→S •
        moved = Item(
            lhs=self.start_prime,
            rhs=[self.grammar.start_symbol],
            dot=1
        )
        self.assertIn(moved, g)

if __name__ == "__main__":
    unittest.main()
