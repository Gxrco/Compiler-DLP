# Compiler-DLP Project

This project is a comprehensive implementation of a compiler for a custom language, focusing on lexical and syntactic analysis. It is divided into multiple modules, each responsible for a specific aspect of the compilation process.

## Project Structure

The project is organized into the following directories:

- **YALex/**: Contains tools and scripts for lexical analysis, including a lexer generator and utilities for processing `.yal` files.
- **YAPar/**: Implements the parser for syntactic analysis, including grammar parsing, LR(0) and SLR table generation, and parsing engines.
- **afd_compiler/**: Handles the construction and optimization of Deterministic Finite Automata (DFA) for token recognition.
- **chain_compiler/**: Provides utilities for processing regular expressions, generating Abstract Syntax Trees (AST), and converting them into DFA.
- **lex_compiler/**: Contains services related to lexical compilation.
- **tests/**: Includes unit tests for various components of the project.

## Key Features

### 1. Lexical Analysis with YALex
- Define tokens and rules in `.yal` files.
- Generate a lexer using the `app.py` script in the `YALex` directory.
- Supports tokenization of input files based on the defined rules.

### 2. Syntactic Analysis with YAPar
- Parse grammar definitions and generate parsing tables.
- Supports LR(0) and SLR parsing techniques.
- Includes utilities for grammar AST manipulation and table generation.

### 3. DFA Construction and Optimization
- Build DFA from regular expressions using ASTs.
- Optimize DFA using minimization algorithms for efficient token recognition.

### 4. Modular Design
- Each component is modular and reusable, allowing for easy integration and extension.
- Clear separation of concerns between lexical and syntactic analysis.

## How to Use

### Generating a Lexer
1. Define your tokens and rules in a `.yal` file (e.g., `YALex/ejemplo3.yal`).
2. Run the following command to generate a lexer:
  ```bash
  python YALex/app.py --yal YALex/ejemplo3.yal --out YALex/thelexer.py
  ```

### Scanning an Input File
Use the generated lexer to scan an input file.

### Parsing a Grammar
1. Define your grammar in a `.yalp` file (e.g., `YAPar/examples/demo.yalp`).
2. Use the YAPar tools to generate parsing tables and parse input files.

### Example Workflow
1. Define tokens in a `.yal` file.
2. Generate a lexer using `YALex/app.py`.
3. Define grammar rules in a `.yalp` file.
4. Generate parsing tables using YAPar.
5. Use the lexer and parser to analyze input files.

## Requirements
- Python 3.8 or higher
- Dependencies listed in `requirements.txt` (if available)

## Running Tests
To run the unit tests for the project, navigate to the `tests/` directory and execute:
```bash
pytest
```

## Acknowledgments
This project was developed as part of the CC3071 - Compiler Design course at UVG. Special thanks to the course instructors and teaching assistants for their guidance.