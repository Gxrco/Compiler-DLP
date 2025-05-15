# YAPar/tests/test_cli_integration.py

import os
import sys
import subprocess
import tempfile
import unittest

class CLIIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Raíz del proyecto (dos niveles arriba de este archivo)
        cls.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )
        cls.grammar = os.path.join(
            cls.project_root, 'YAPar', 'examples', 'demo.yalp'
        )

    def test_help_shows_usage(self):
        result = subprocess.run(
            [sys.executable, '-m', 'YAPar.cli', '--help'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage', result.stdout.lower())

    def test_generate_parser_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_file = os.path.join(tmp, 'cli_parser.py')
            result = subprocess.run(
                [sys.executable, '-m', 'YAPar.cli',
                 self.grammar, '-o', out_file],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(out_file))
            content = open(out_file, encoding='utf-8').read()
            self.assertIn('ACTION =', content)
            self.assertIn('GOTO =', content)

    def test_cli_test_mode_parses_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Crear archivo de tokens de prueba
            input_file = os.path.join(tmp, 'tokens.txt')
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write('ID PLUS ID')
            # Llamar al CLI con --test
            result = subprocess.run(
                [sys.executable, '-m', 'YAPar.cli',
                 self.grammar, '-o', os.path.join(tmp, 'out.py'),
                 '--test', input_file],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0)
            # Debe mostrar acciones shift y accept
            self.assertIn('shift ID', result.stdout)
            self.assertIn('accept', result.stdout)

if __name__ == "__main__":
    unittest.main()
