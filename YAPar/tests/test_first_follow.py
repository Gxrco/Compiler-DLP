import os
import unittest
from YAPar.grammar_parser import parse_file
from YAPar.utils.first_follow import compute_first, compute_follow

class FirstFollowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Gramática de ejemplo incluida en el repo
        here = os.path.dirname(__file__)
        demo_path = os.path.normpath(
            os.path.join(here, "..", "examples", "demo.yalp")
        )
        cls.grammar = parse_file(demo_path)

    def test_compute_first_returns_dict(self):
        first = compute_first(self.grammar)
        # Debe devolver un dict cuyos keys sean símbolos de la gramática
        self.assertIsInstance(first, dict)
        self.assertIn(self.grammar.start_symbol, first)

    def test_first_of_terminal_is_itself(self):
        first = compute_first(self.grammar)
        for t in self.grammar.terminals:
            self.assertEqual(first[t], {t})

    def test_compute_follow_returns_dict(self):
        first = compute_first(self.grammar)
        follow = compute_follow(self.grammar, first)
        self.assertIsInstance(follow, dict)
        # El símbolo inicial debe contener el EOF en FOLLOW
        self.assertIn(self.grammar.eof_token, follow[self.grammar.start_symbol])

    # Aquí podrías añadir más tests puntuales, por ejemplo:
    # - FIRST de un no-terminal concreto
    # - FOLLOW de un no-terminal concreto

if __name__ == "__main__":
    unittest.main()
