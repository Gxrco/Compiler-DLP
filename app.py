import argparse, re
from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService
from file_processor import read_regex_from_file
from chain_compiler.tools.yal_parser import parse_yal_file
from chain_compiler.tools.super_regex_builder import build_super_regex

def scan_input_file(filepath, yal_rules):
    patterns = []
    for regex, tok in yal_rules:
        clean = regex.strip().replace("'", "").replace('"', "")
        try:
            pattern = re.compile(rf'^{clean}')
        except re.error:
            pattern = re.compile(rf'^{re.escape(clean)}')
        patterns.append((pattern, tok))

    symbol_table = []
    with open(filepath, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            pos = 0
            while pos < len(line):
                best = None
                for pat, tok in patterns:
                    m = pat.match(line[pos:])
                    if m and (not best or len(m.group(0)) > len(best[0])):
                        best = (m.group(0), tok)
                if best:
                    lex, token = best
                    if token != "lexbuf":
                        symbol_table.append({"line": lineno, "token": token, "lexeme": lex})
                    pos += len(lex)
                else:
                    symbol_table.append({"line": lineno, "token": "ERROR", "lexeme": line[pos]})
                    pos += 1

    print("\nTabla de símbolos:")
    for entry in symbol_table:
        print(entry)




def process_regex(super_regex, test_strings=None):
    print("Expresión regular:", super_regex)
    tokens=normalize_regex(super_regex)
    postfix=parse_tokens(tokens)
    ast=generate_ast(postfix)
    print(ast.pretty_print())
    graph=build_ast_graph(ast); graph.render('ast_graph',view=False)
    afd=AFDService(); afd.build_dfa_from_ast(ast)
    afd.minimize_dfa()
    return afd

def process_yal_file(path, scan_file=None):
    info=parse_yal_file(path)
    if not info: return
    print("Header:\n",info.get("header",""))
    print("Rule:", info["rule"])
    print("Alternativas:")
    for r,a in info["alternatives"]: print(f"  {r} => {a}")
    print("Trailer:\n",info.get("trailer",""))

    yal_rules = []
    for regex, action in info["alternatives"]:
        # Extraer token: primero busca return "TOKEN" o return 'TOKEN'
        m = re.search(r'return\s+[\'"]([^\'"]+)[\'"]', action)
        if m:
            token = m.group(1)
        elif "return" in action:
            # Si no hay comillas, toma la función (int, etc.) como token
            token = re.match(r'return\s*([A-Za-z_]\w*)', action).group(1).upper()
        elif "raise" in action:
            token = "EOF"
        else:
            token = "UNKNOWN"

        # Limpiar el patrón — quitar comillas internas, mantener clases intactas
        clean = regex.strip().replace("'", "").replace('"', "")
        yal_rules.append((clean, token))

    
    super_regex=build_super_regex(info["alternatives"])
    afd=process_regex(super_regex)
    if scan_file:
        scan_input_file(scan_file, yal_rules)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--yal'); p.add_argument('--scan_file')
    args=p.parse_args()
    if args.yal:
        process_yal_file(args.yal, args.scan_file)
    else:
        print("Use --yal <archivo>.")