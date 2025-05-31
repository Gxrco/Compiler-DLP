#!/usr/bin/env python3

import sys
import importlib.util

def import_module(file_path):
    """Import a Python module from file path"""
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def print_valid_tokens_for_state(parser_module, state):
    """Print all valid tokens for a given state"""
    print(f"\nValid tokens in state {state}:")
    valid_tokens = []
    for (s, token), action in parser_module.ACTION.items():
        if s == state:
            valid_tokens.append(f"'{token}' -> {action}")
    
    for token in sorted(valid_tokens):
        print(f"  {token}")

def print_productions(parser_module):
    """Print all productions in the grammar"""
    print("\nProductions:")
    for i, (lhs, rhs_list) in enumerate(parser_module.PRODUCTIONS):
        for rhs in rhs_list:
            print(f"  {i}: {lhs} -> {' '.join(rhs)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: ./debug_parser.py <parser_module.py> [state_number]")
        sys.exit(1)
    
    import os
    parser_path = sys.argv[1]
    state = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    try:
        parser_module = import_module(parser_path)
        print_productions(parser_module)
        print_valid_tokens_for_state(parser_module, state)
        
        # Print the first few entries in ACTION and GOTO tables
        print("\nSample of ACTION table:")
        count = 0
        for key, value in parser_module.ACTION.items():
            print(f"  {key}: {value}")
            count += 1
            if count >= 10:
                print("  ...")
                break
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
