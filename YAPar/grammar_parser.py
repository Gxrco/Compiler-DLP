# YAPar/grammar_parser.py

import re
from YAPar.grammar_ast import Grammar, Production
from typing import List, Tuple

def remove_comments(text: str) -> str:
    """
    Elimina todos los comentarios delimitados por /* ... */ (multilínea).
    """
    pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
    return re.sub(pattern, '', text)

def split_sections(text: str) -> Tuple[List[str], List[str]]:
    """
    Divide el archivo en dos listas de líneas, cortando en la línea que contiene '%%'.
    Devuelve (lines_tokens_section, lines_productions_section).
    """
    lines = text.splitlines()
    try:
        idx = next(i for i, l in enumerate(lines) if l.strip() == '%%')
    except StopIteration:
        raise ValueError("No se encontró la línea '%%' para separar secciones")
    tokens_sec = lines[:idx]
    prods_sec  = lines[idx+1:]
    return tokens_sec, prods_sec

def parse_tokens_section(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    De una lista de líneas de la sección de tokens:
      - extrae todos los identificadores tras '%token'
      - extrae la lista tras 'IGNORE'
    devuelve (tokens, ignore_list)
    """
    tokens = []
    ignore = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if parts[0] == '%token':
            tokens += parts[1:]
        elif parts[0] == 'IGNORE':
            ignore += parts[1:]
    return tokens, ignore

def parse_productions_section(lines: List[str]) -> List[Production]:
    """
    De una lista de líneas de producciones construye la lista de Production.
    Cada producción termina en ';'. Se agrupan líneas entre ':' y ';'.
    """
    prods: List[Production] = []
    buffer = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        buffer.append(line)
        if line.endswith(';'):
            # unir buffer y parsear
            block = " ".join(buffer)[:-1]  # quita el ';'
            buffer.clear()
            # lhs: antes de ':'
            if ':' not in block:
                raise ValueError(f"Producción inválida (falta ':'): {block}")
            lhs, rhs = block.split(':', 1)
            lhs = lhs.strip()
            # cada alternativa separada por '|'
            alts = [alt.strip().split() for alt in rhs.split('|')]
            prods.append(Production(lhs, alts))
    return prods

def parse_file(path: str) -> Grammar:
    """
    Lee un archivo .yalp, parsea y devuelve una instancia de Grammar.
    """
    text = open(path, encoding='utf-8').read()
    text_noc = remove_comments(text)
    tok_lines, prod_lines = split_sections(text_noc)
    tokens, ignore = parse_tokens_section(tok_lines)
    prods = parse_productions_section(prod_lines)
    return Grammar(tokens, ignore, prods)
