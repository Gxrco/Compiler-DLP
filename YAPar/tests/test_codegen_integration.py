# YAPar/tests/test_codegen_integration.py

import os
import sys
import tempfile
import importlib.util
import unittest

from YAPar.codegen.generator import generate_parser

class CodegenIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', 'examples', 'demo.yalp')
        )

    def test_generate_parser_file_and_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_file = os.path.join(tmp, 'testparser.py')
            # Generar parser
            generate_parser(self.grammar, out_file)
            # El archivo debe existir
            self.assertTrue(os.path.exists(out_file))
            # Comprobar sintaxis e importar
            spec = importlib.util.spec_from_file_location("testparser", out_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Debe exponer PRODUCTIONS, ACTION, GOTO y función parse
            self.assertTrue(hasattr(module, 'PRODUCTIONS'))
            self.assertIsInstance(module.PRODUCTIONS, list)
            self.assertTrue(hasattr(module, 'ACTION'))
            self.assertIsInstance(module.ACTION, dict)
            self.assertTrue(hasattr(module, 'GOTO'))
            self.assertIsInstance(module.GOTO, dict)
            self.assertTrue(callable(module.parse))


if __name__ == "__main__":
    unittest.main()
