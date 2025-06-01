#!/usr/bin/env python3

import sys
import os

# Agregar YALex al path
yalex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "YALex")
if yalex_dir not in sys.path:
    sys.path.insert(0, yalex_dir)

def test_lexer(input_text):
    """Prueba el lexer con una entrada específica"""
    print("\n=== TEST LEXER ===")
    print(f"Entrada: {repr(input_text)}")
    
    try:
        import thelexer
        tokens = thelexer.entrypoint(input_text)
        print("\nTokens generados:")
        for i, (tok, lex) in enumerate(tokens):
            print(f"  {i:3d}: {tok:15} '{lex}'")
        return tokens
    except Exception as e:
        print(f"Error en lexer: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_parser(tokens):
    """Prueba el parser con una lista de tokens"""
    print("\n=== TEST PARSER ===")
    print(f"Tokens de entrada: {[t for t,_ in tokens]}")
    
    try:
        import theparser
        # Extraer solo los nombres de los tokens
        token_names = [tok for tok, _ in tokens]
        result = theparser.parse(token_names)
        
        print("\nAcciones del parser:")
        for state, action in result:
            print(f"  Estado {state}: {action}")
        
        if result and result[-1][1] == 'accept':
            print("\n✅ Parsing exitoso!")
        else:
            print("\n⚠️ No se llegó a 'accept'")
        
        return result
    except Exception as e:
        print(f"\n❌ Error en parser: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    # Casos de prueba
    test_cases = [
        # Caso 1: Asignación simple
        "x = 5;",
        
        # Caso 2: If simple
        "if (x > 0): { y = 1; }",
        
        # Caso 3: While simple
        "while (x > 0): { x = x - 1; }",
        
        # Caso 4: Expresión compleja
        "result = (a + b) * (c - d);",
        
        # Caso 5: Programa completo simple
        """x = 5;
if (x > 0): {
    y = x + 1;
}""",
    ]
    
    for i, test_input in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"CASO DE PRUEBA {i+1}")
        print(f"{'='*60}")
        
        tokens = test_lexer(test_input)
        if tokens:
            test_parser(tokens)

if __name__ == "__main__":
    # Si se proporciona un archivo como argumento, usarlo
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            test_input = f.read()
        print(f"\nProbando con archivo: {sys.argv[1]}")
        tokens = test_lexer(test_input)
        if tokens:
            test_parser(tokens)
    else:
        # Ejecutar casos de prueba predefinidos
        main()