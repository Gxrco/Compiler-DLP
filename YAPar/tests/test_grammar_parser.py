# YAPar/tests/test_grammar_parser.py

import unittest
import os
from YAPar.grammar_parser import parse_file

class GrammarParserTest(unittest.TestCase):
    def test_demo_grammar(self):
        # Calculamos la ruta de demo.yalp relativa a este archivo
        here = os.path.dirname(__file__)
        demo_path = os.path.normpath(os.path.join(here, "..", "examples", "demo.yalp"))

        # Parseamos la gramática
        grammar = parse_file(demo_path)

        # Aserciones básicas
        self.assertTrue(len(grammar.tokens) > 0, "No se detectaron tokens")
        self.assertTrue(len(grammar.ignore) >= 0, "Campo ignore debe existir")
        self.assertTrue(len(grammar.productions) > 0, "No se detectaron producciones")

        # Comprobamos que 'expression' está entre los lhs de las producciones
        lhs_list = [prod.lhs for prod in grammar.productions]
        self.assertIn("expression", lhs_list)

if __name__ == "__main__":
    unittest.main()
