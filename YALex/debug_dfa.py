# debug_dfa.py

from chain_compiler.tools.yal_parser       import parse_yal_file
from chain_compiler.tools.super_regex_builder import build_super_regex
from chain_compiler.normalizer             import normalize_regex
from chain_compiler.parser                 import parse_tokens
from chain_compiler.ast_service            import generate_ast
from afd_compiler.service                  import AFDService

# 1) Parsear el .yal
info = parse_yal_file("ejemplo3.yal")
alts = info["alternatives"]
print("Alternativas detectadas:", [pat for pat,_ in alts])

# 2) Generar super-regex + token_names
super_regex, token_names = build_super_regex(alts)
print("Token names:", token_names)

# 3) De la regex al AST
tokens_norm = normalize_regex(super_regex)
postfix     = parse_tokens(tokens_norm)
ast         = generate_ast(postfix)

# 4) Construir el DFA sin minimizarlo
afd_svc = AFDService()
dfa = afd_svc.build_dfa_from_ast(ast, token_names)

# 5) Inspección de estado: ¿qué mapeo tenemos?
print("\n=== state_tokens BEFORE minimize ===")
for state, tok in dfa.state_tokens.items():
    print(f"  State {state}  →  Token {tok!r}")

# Después de dfa = afd_svc.minimize_dfa()
print("\n=== state_tokens AFTER minimize ===")
for state, tok in dfa.state_tokens.items():
    print(f"  State {state}  →  Token {tok!r}")
