# YAPar/grammar_parser.py

import re
from typing import List
from .grammar_ast import Grammar, Production

TOKEN_RE   = re.compile(r'^\s*%token\s+(.+)$')
IGNORE_RE  = re.compile(r'^\s*IGNORE\s+(.+)$')
SEP_RE     = re.compile(r'^\s*%%\s*$')
PROD_HEAD  = re.compile(r'^\s*(\w+)\s*:\s*(.*)$')
ALT_SPLIT  = re.compile(r'\s*\|\s*')
END_PROD   = re.compile(r';\s*$')

def parse_file(path: str) -> Grammar:
    tokens: List[str] = []
    ignore: List[str] = []
    productions: List[Production] = []

    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()

    phase = 'tokens'  # fases: tokens, prods
    i = 0
    # ——— Sección de TOKENS / IGNORE ———
    while i < len(lines):
        line = lines[i].strip()
        if SEP_RE.match(line):
            phase = 'prods'
            i += 1
            break

        m_tok = TOKEN_RE.match(line)
        m_ign = IGNORE_RE.match(line)
        if m_tok:
            # extraer todos los tokens separados por espacio
            tokens += m_tok.group(1).split()
        elif m_ign:
            ignore += m_ign.group(1).split()
        # else: comentario o vacío → ignorar
        i += 1

    # ——— Sección de PRODUCCIONES ———
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('/*'):
            i += 1
            continue

        # producción puede abarcar varias líneas hasta ;
        prod_lines = []
        while i < len(lines):
            prod_lines.append(lines[i].strip())
            if END_PROD.search(lines[i]):
                break
            i += 1
        prod_text = " ".join(prod_lines)
        i += 1

        # extraer nombre y RHS completo (sin ;)
        m_head = PROD_HEAD.match(prod_text)
        if not m_head:
            continue
        lhs = m_head.group(1)
        rhs_all = m_head.group(2).rstrip(';').strip()

        # dividir alternativas
        alts = ALT_SPLIT.split(rhs_all)
        rhs_list = []
        for alt in alts:
            symbols = [tok for tok in alt.split() if tok]
            rhs_list.append(symbols)
        productions.append(Production(lhs=lhs, rhs=rhs_list))

    return Grammar(tokens=tokens, ignore=ignore, productions=productions)
