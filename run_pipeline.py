#!/usr/bin/env python3

import sys
import os
import subprocess
import importlib.util

def generate_lexer(yal_file, output_file="thelexer.py"):
    """Generate the lexer using YALex"""
    print(f"\n=== 1) Generando {output_file} desde {yal_file} ===")
    result = subprocess.run(
        ["python", "-m", "YALex.app", "--yal", yal_file, "--out", output_file],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error generando lexer: {result.stderr}")
        sys.exit(1)

def generate_parser(yalp_file, output_file="theparser.py"):
    """Generate the parser using YAPar"""
    print(f"\n=== 2) Generando {output_file} & lr0_states.pdf desde {yalp_file} ===")
    result = subprocess.run(
        ["python", "-m", "YAPar.cli", yalp_file, "-o", output_file, "--visualize"],
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
    setup_path()  # Add YALex directory to sys.path
    lexer_module = import_module("thelexer.py")
    parser_module = import_module("theparser.py")
    
    # 4. Read input file
    print(f"\n=== 4) Leyendo entrada: {input_file} ===")
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    
    # 5. Tokenize the input
    print("\n=== 5) Tokenizando con thelexer.entrypoint() ===")
    token_lexeme_pairs = lexer_module.entrypoint(input_text)
    
    # Extract just the token names (without lexemes)
    tokens = [token for token, lexeme in token_lexeme_pairs]
    print("Tokens generados:")
    print(tokens)
    
    # 6. Parse the tokens
    print("\n=== 6) Parseando con theparser.parse() ===")
    try:
        # Examine the first valid actions in state 0
        valid_actions_state0 = [(token, action) for (state, token), action in parser_module.ACTION.items() if state == 0]
        print(f"Acciones válidas en el estado inicial (0):")
        for token, action in valid_actions_state0:
            print(f"  Token '{token}' -> {action}")
        
        # Try parsing with verbose error handling
        parse_result = parser_module.parse(tokens)
        print("\nParsing exitoso!")
        print("Acciones de parseo:")
        for state, action in parse_result:
            print(format_action(state, action))
    except Exception as e:
        print(f"Error de parseo: {e}")
        
        # Additional debugging info on error
        print("\nDebugging info:")
        if tokens:
            first_token = tokens[0]
            print(f"Primer token: '{first_token}'")
            valid_tokens = [token for (state, token), _ in parser_module.ACTION.items() if state == 0]
            print(f"Tokens esperados en estado 0: {valid_tokens}")
            
            # Suggest fix
            print("\nPosible solución:")
            print("1. Revise el archivo de gramática para asegurarse que los comentarios")
            print("   están marcados correctamente y no son tratados como parte de la gramática.")
            print("2. Ejecute ./debug_parser.py theparser.py para ver detalles del parser.")

if __name__ == "__main__":
    main()
