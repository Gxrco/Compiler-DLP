# debug_pipeline.py

from chain_compiler.tools.yal_parser       import parse_yal_file
from chain_compiler.tools.super_regex_builder import build_super_regex
from chain_compiler.normalizer             import normalize_regex
from chain_compiler.parser                 import parse_tokens
from chain_compiler.ast_service            import generate_ast
from afd_compiler.service                  import AFDService

# Paso 1: Parsear .yal y construir super-regex
info = parse_yal_file("ejemplo3.yal")
alts = info["alternatives"]
print("⎯⎯ Alternatives:", alts)
super_regex, token_names = build_super_regex(alts)
print("⎯⎯ Token names:", token_names)
print("⎯⎯ Super-regex:", super_regex, "\n")

# Paso 2: Normalizar la regex
tokens_norm = normalize_regex(super_regex)
print("⎯⎯ normalize_regex →", tokens_norm, "\n")

# Paso 3: Convertir a postfix
postfix = parse_tokens(tokens_norm)
print("⎯⎯ parse_tokens (postfix) →", [t.value if hasattr(t, "value") else t for t in postfix], "\n")

# Paso 4: Generar AST y visualizar
ast = generate_ast(postfix)
print("⎯⎯ AST pretty_print:\n", ast.pretty_print(), "\n")

# Paso 5: Construir DFA sin minimizar
afd_svc = AFDService()
dfa = afd_svc.build_dfa_from_ast(ast, token_names)
print("⎯⎯ DFA alphabet (len={}): {}".format(len(dfa.alphabet), sorted(dfa.alphabet)))
print("⎯⎯ state_tokens BEFORE minimize:")
for state, tok in dfa.state_tokens.items():
    print(f"    {state!r}  →  {tok!r}")
print()

# Paso 6: Minimizar DFA y re-inspeccionar
dfa_min = afd_svc.minimize_dfa()
print("⎯⎯ state_tokens AFTER minimize:")
for state, tok in dfa_min.state_tokens.items():
    print(f"    {state!r}  →  {tok!r}")
print()

# Paso 7: Probar match() en ejemplos unitarios
print("⎯⎯ Pruebas de AFDService.match():")
for ejemplo in ["if", "else", "+", "-", "(", ")", "#comentario", "foo", "123", " "]:
    print(f"  match({ejemplo!r}) →", afd_svc.match(ejemplo))
print()

# Paso 8: Probar scan_input() con un mini-buffer
print("⎯⎯ Prueba scan_input(\"if a + 1 # fin\") →")
print(afd_svc.scan_input("if a + 1 # fin"))
