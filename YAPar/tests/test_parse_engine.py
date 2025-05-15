import os
import unittest

from YAPar.parse_engine import parse_tokens, ParseError

class ParseEngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(__file__)
        cls.demo = os.path.normpath(os.path.join(here, "..", "examples", "demo.yalp"))

    def test_accepting_sequence(self):
        # Para la entrada "ID PLUS ID", que en tokens sería:
        tokens = ['ID', 'PLUS', 'ID']
        actions = parse_tokens(self.demo, tokens)
        # La última acción debe ser 'accept'
        self.assertTrue(actions[-1][1] == 'accept')

    def test_simple_reduce(self):
        # Para "ID", en la gramática factor->ID produce un reduce
        tokens = ['ID']
        actions = parse_tokens(self.demo, tokens)
        # Busca al menos una acción 'reduce factor -> ID'
        reduces = [desc for _, desc in actions if desc.startswith('reduce factor -> ID')]
        self.assertTrue(len(reduces) >= 1)

    def test_unexpected_token(self):
        # Un token no reconocido debe lanzar ParseError
        with self.assertRaises(ParseError):
            parse_tokens(self.demo, ['UNKNOWN_TOKEN'])

if __name__ == "__main__":
    unittest.main()
