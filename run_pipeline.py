#!/usr/bin/env python3

import sys
import os
import subprocess
import importlib.util

def generate_lexer(yal_file, output_file="thelexer.py"):
    """Generate the lexer using YALex"""
    print(f"\n=== 1) Generando {output_file} desde {yal_file} ===")
    result = subprocess.run(
        [sys.executable, "-m", "YALex.app", "--yal", yal_file, "--out", output_file],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error generando lexer: {result.stderr}")
        sys.exit(1)

def generate_parser(yalp_file, output_file="theparser.py"):
    """Generate the parser using YAPar"""
    print(f"\n=== 2) Generando {output_file} desde {yalp_file} ===")
    result = subprocess.run(
        [sys.executable, "-m", "YAPar.cli", yalp_file, "-o", output_file],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error generando parser: {result.stderr}")
        sys.exit(1)

def setup_path():
    """Add YALex to the Python path to find chain_compiler and afd_compiler modules"""
    yalex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "YALex")
    if yalex_dir not in sys.path:
        sys.path.insert(0, yalex_dir)
    print(f"Python path modificado: YALex añadido a sys.path")

def format_action(state, action):
    """Format an action from the parser for printing"""
    return f"Estado {state}: {action}"

def main():
    if len(sys.argv) < 4:
        print("Uso: ./run_pipeline.py <archivo_yal> <archivo_yalp> <archivo_entrada>")
        sys.exit(1)
    
    yal_file = sys.argv[1]
    yalp_file = sys.argv[2]
    input_file = sys.argv[3]
    
    generate_lexer(yal_file)
    # 2. Generate parser
    generate_parser(yalp_file)
    
    # 3. Setup path
    print("\n=== 3) Configurando path para importación ===")
    setup_path()
    
    # 4. Read input file
    print(f"\n=== 4) Leyendo entrada: {input_file} ===")
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    print(f"Primeros 100 caracteres: {repr(input_text[:100])}")
    
    # 5. Tokenize the input - USANDO IMPORTACIÓN DIRECTA como en test_lexer_parser.py
    print("\n=== 5) Tokenizando con thelexer.entrypoint() ===")
    try:
        # Importación directa como en test_lexer_parser.py
        import thelexer
        tokens = thelexer.entrypoint(input_text)
        
        print("\nTokens generados:")
        for i, (tok, lex) in enumerate(tokens[:15]):  # Mostrar solo los primeros 15 tokens
            print(f"  {i:3d}: {tok:15} '{lex}'")
        
        print(f"\nTotal de tokens: {len(tokens)}")
        
        # 6. Parse the tokens - USANDO IMPORTACIÓN DIRECTA como en test_lexer_parser.py
        print("\n=== 6) Parseando con theparser.parse() ===")
        
        import theparser
        # Extraer solo los nombres de los tokens como en test_lexer_parser.py
        token_names = [tok for tok, _ in tokens]
        
        # Debug: mostrar información sobre la gramática
        print("\nProducciones disponibles:")
        for i, (lhs, rhss) in enumerate(theparser.PRODUCTIONS[:10]):
            for rhs in rhss:
                print(f"  {i}: {lhs} -> {' '.join(rhs) if rhs else '/* empty */'}")
        
        # Debug: mostrar acciones válidas en estado 0
        valid_actions_state0 = [(token, action) for (state, token), action in theparser.ACTION.items() if state == 0]
        print(f"\nAcciones válidas en el estado inicial (0):")
        for token, action in sorted(valid_actions_state0):
            print(f"  Token '{token}' -> {action}")
        
        # Try parsing
        parse_result = theparser.parse(token_names)
        print("\n✅ ¡Parsing exitoso!")
        print("\nPrimeras 10 acciones de parseo:")
        for state, action in parse_result[:10]:
            print(f"  {format_action(state, action)}")
        if len(parse_result) > 10:
            print(f"  ... y {len(parse_result)-10} acciones más")
            
        # Verificar si llegó a accept
        if parse_result and parse_result[-1][1] == 'accept':
            print("\n✅ El parser aceptó la entrada correctamente")
        else:
            print("\n⚠️ El parser no llegó a 'accept'")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()