# YAPar/grammar_parser.py

import re
from typing import List
from .grammar_ast import Grammar, Production
from YAPar.errors import GrammarError

TOKEN_RE   = re.compile(r'^\s*%token\s+(.+)$')
IGNORE_RE  = re.compile(r'^\s*IGNORE\s+(.+)$')
SEP_RE     = re.compile(r'^\s*%%\s*$')
PROD_HEAD  = re.compile(r'^\s*(\w+)\s*:\s*(.*)$')
ALT_SPLIT  = re.compile(r'\s*\|\s*')
END_PROD   = re.compile(r';\s*$')

def parse_file(path: str) -> Grammar:
    """
    Lee y parsea una gramática YAPar (.yalp), devolviendo un objeto Grammar.
    Lanza GrammarError si falla la lectura o la sintaxis.
    """
    tokens: List[str] = []
    ignore: List[str] = []
    productions: List[Production] = []

    # 1) Leer el archivo
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise GrammarError(f"No se puede leer el archivo de gramática '{path}': {e}")

    # 2) Fase de tokens y ignore
    phase = 'tokens'
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if SEP_RE.match(line):
            phase = 'prods'
            i += 1
            break

        m_tok = TOKEN_RE.match(line)
        m_ign = IGNORE_RE.match(line)
        if m_tok:
            tokens += m_tok.group(1).split()
        elif m_ign:
            ignore += m_ign.group(1).split()
        # líneas vacías o comentarios se ignoran
        i += 1

    # 3) Fase de producciones
    while i < len(lines):
        raw = lines[i].strip()
        if not raw or raw.startswith('/*'):
            i += 1
            continue

        # Acumular líneas hasta encontrar ';'
        prod_lines = []
        while i < len(lines):
            prod_lines.append(lines[i].strip())
            if END_PROD.search(lines[i]):
                break
            i += 1
        prod_text = " ".join(prod_lines)
        i += 1

        # Extraer lhs y rhs
        m_head = PROD_HEAD.match(prod_text)
        if not m_head:
            # Si no coincide el patrón, es sintaxis inválida
            raise GrammarError(f"Línea de producción inválida: '{prod_text}'")
        lhs = m_head.group(1)
        rhs_all = m_head.group(2).rstrip(';').strip()

        # Dividir alternativas por '|'
        parts = ALT_SPLIT.split(rhs_all)
        rhs_list: List[List[str]] = []
        for part in parts:
            symbols = [tok for tok in part.strip().split() if tok]
            if not symbols:
                # Producción vacía (ε)
                rhs_list.append([])
            else:
                rhs_list.append(symbols)

        productions.append(Production(lhs=lhs, rhs=rhs_list))

    # 4) Construir y devolver la Grammar
    try:
        return Grammar(tokens=tokens, ignore=ignore, productions=productions)
    except Exception as e:
        raise GrammarError(f"Error al construir el objeto Grammar: {e}")
