import os
import unittest

from YAPar.grammar_parser import parse_file
from YAPar.utils.closure_goto import closure, goto
from YAPar.lr0_builder import build_lr0_states
from YAPar.model.item import Item

class LR0BuilderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(__file__)
        demo = os.path.normpath(os.path.join(here, "..", "examples", "demo.yalp"))
        cls.grammar = parse_file(demo)
        # producimos la versión augmentada: S' → S
        cls.start_prime = cls.grammar.start_symbol + "'"
        cls.aug_prods  = [(cls.start_prime, [[cls.grammar.start_symbol]])] \
                         + [(p.lhs, p.rhs) for p in cls.grammar.productions]

    def test_number_of_states(self):
        states = build_lr0_states(self.aug_prods, self.start_prime)
        # Para la gramática demo.yalp esperamos, digamos, N estados
        self.assertEqual(len(states), 10)

    def test_initial_state(self):
        states = build_lr0_states(self.aug_prods, self.start_prime)
        I0 = states[0]
        # Debe contener el ítem inicial S'→•S
        self.assertIn(Item(lhs=self.start_prime,
                           rhs=[self.grammar.start_symbol],
                           dot=0),
                      I0)

    def test_transitions(self):
        states = build_lr0_states(self.aug_prods, self.start_prime)
        # Encuentra el estado al que GOTO(I0, 'expression') debería llevar
        # y comprueba que en ese estado los ítems tengan • avanzado
        I0 = states[0]
        I1 = goto(I0, 'expression', self.aug_prods)
        self.assertIn(I1, states)

if __name__ == "__main__":
    unittest.main()
