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
    # Omitir --visualize si causa problemas
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

def import_module(file_path):
    """Import a Python module from file path"""
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def format_action(state, action):
    """Format an action from the parser for printing"""
    return f"Estado {state}: {action}"

def debug_tokens(tokens, lexeme_pairs):
    """Print detailed token information for debugging"""
    print("\n=== DEBUG: Tokens detallados ===")
    for i, ((tok, lex), tok_only) in enumerate(zip(lexeme_pairs[:10], tokens[:10])):
        print(f"{i}: Token='{tok}', Lexeme='{lex}', Token_only='{tok_only}'")
    if len(tokens) > 10:
        print(f"... y {len(tokens)-10} tokens más")

def main():
    if len(sys.argv) < 4:
        print("Uso: ./run_pipeline.py <archivo_yal> <archivo_yalp> <archivo_entrada>")
        sys.exit(1)
    
    yal_file = sys.argv[1]
    yalp_file = sys.argv[2]
    input_file = sys.argv[3]
    
    # 1. Generate lexer
    generate_lexer(yal_file)
    
    # 2. Generate parser
    generate_parser(yalp_file)
    
    # 3. Setup path and import the generated modules
    print("\n=== 3) Importando módulos ===")
    setup_path()
    lexer_module = import_module("thelexer.py")
    parser_module = import_module("theparser.py")
    
    # 4. Read input file
    print(f"\n=== 4) Leyendo entrada: {input_file} ===")
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    print(f"Primeros 100 caracteres: {repr(input_text[:100])}")
    
    # 5. Tokenize the input
    print("\n=== 5) Tokenizando con thelexer.entrypoint() ===")
    token_lexeme_pairs = lexer_module.entrypoint(input_text)
    
    # Debug: mostrar los primeros tokens con sus lexemas
    print("\nInspección detallada de tokens:")
    for i, (tok, lex) in enumerate(token_lexeme_pairs[:15]):
        print(f"  Token {i}: '{tok}' - Lexema: '{lex}'")
    
    # Extract just the token names
    tokens = [token for token, lexeme in token_lexeme_pairs]
    print(f"\nTotal de tokens: {len(tokens)}")
    
    # 6. Parse the tokens
    print("\n=== 6) Parseando con theparser.parse() ===")
    try:
        # Debug: mostrar producciones disponibles
        print("\nProducciones disponibles:")
        for i, (lhs, rhss) in enumerate(parser_module.PRODUCTIONS[:5]):
            for rhs in rhss:
                print(f"  {i}: {lhs} -> {' '.join(rhs) if rhs else 'ε'}")
        
        # Debug: mostrar acciones válidas en estado 0
        valid_actions_state0 = [(token, action) for (state, token), action in parser_module.ACTION.items() if state == 0]
        print(f"\nAcciones válidas en el estado inicial (0):")
        for token, action in sorted(valid_actions_state0):
            print(f"  Token '{token}' -> {action}")
        
        # Try parsing
        parse_result = parser_module.parse(tokens)
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
            print("\n⚠️  El parser no llegó a 'accept'")
            
    except Exception as e:
        print(f"\n❌ Error de parseo: {e}")
        
        # Debugging adicional
        print("\n=== Información de debugging ===")
        if tokens:
            print(f"Secuencia inicial de tokens: {tokens[:5]}")
            print(f"Primer token problemático: '{tokens[0]}' (esperando: IF, WHILE, ID, LBRACE)")
            
            # Si el problema es con múltiples IDs consecutivos
            if len(tokens) > 1 and tokens[0] == 'ID' and tokens[1] == 'ID':
                print("\n⚠️  Detectados múltiples tokens ID consecutivos.")
                print("Esto sugiere que el lexer está tokenizando carácter por carácter.")
                print("Verifique que el archivo .yal tenga las reglas correctas para identificadores.")

if __name__ == "__main__":
    main()
