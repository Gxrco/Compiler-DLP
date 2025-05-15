# YAPar/tests/test_slr_table_generator.py

import os
import unittest

from YAPar.slr_table_generator import build_slr_parsing_table
from YAPar.grammar_parser         import parse_file
from YAPar.model.item            import Item

class SLRTableGeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(__file__)
        demo = os.path.normpath(os.path.join(here, "..", "examples", "demo.yalp"))
        cls.states, cls.action, cls.goto = build_slr_parsing_table(demo)
        cls.grammar = parse_file(demo)
        cls.EOF     = cls.grammar.eof_token

    def test_states_count(self):
        # Con demo.yalp deberíamos tener 10 estados
        self.assertEqual(len(self.states), 10)

    def test_shift_on_ID(self):
        # Desde el estado 0, al ver 'ID' debe haber un shift
        act = self.action.get((0, 'ID'))
        self.assertIsNotNone(act)
        self.assertEqual(act[0], 'shift')

    def test_goto_expression(self):
        # Desde el estado 0, GOTO con 'expression' lleva al estado 1
        self.assertEqual(self.goto.get((0, 'expression')), 1)

    def test_reduce_on_factor(self):
        # Hay un reduce por la producción factor -> ID (índice 2 en prods)
        reduce_actions = [v for v in self.action.values() if v[0]=='reduce']
        # Busca al menos un reduce con indice 2
        self.assertIn(('reduce', 2), reduce_actions)

    def test_accept(self):
        # Debe existir un accept sobre EOF en algún estado
        accepts = [k for k,v in self.action.items() if v[0]=='accept' and k[1]==self.EOF]
        self.assertTrue(len(accepts) == 1)

if __name__ == "__main__":
    unittest.main()
