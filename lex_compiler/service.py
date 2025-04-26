# lex_compiler/service.py
from chain_compiler.tools.super_regex_builder import build_super_regex

def generate_lexer_py(yal_info: dict, output_path: str):
    """
    Genera un archivo .py que implemente el lexer definido en yal_info,
    usando el DFA interno para el escaneo.
    """
    header       = yal_info.get('header', '').strip()
    trailer      = yal_info.get('trailer', '').strip()
    alternatives = yal_info.get('alternatives', [])

    # 1) Construir super-regex **y** token_names
    super_regex, token_names = build_super_regex(alternatives)
    # Quitar saltos de línea reales y reemplazarlos por '\n' literales
    super_regex = super_regex.replace('\r', '').replace('\n', r'\n')

    with open(output_path, 'w', encoding='utf-8') as f:
        # --- Cabecera del usuario ---
        if header:
            f.write(header + "\n\n")

        # --- Definir token_names y super_regex ---
        f.write(f"token_names = {token_names!r}\n")
        f.write(f"super_regex = r'''{super_regex}'''\n\n")

        # --- Importaciones internas ---
        f.write("from chain_compiler.normalizer import normalize_regex\n")
        f.write("from chain_compiler.parser     import parse_tokens\n")
        f.write("from chain_compiler.ast_service import generate_ast\n")
        f.write("from afd_compiler.service       import AFDService\n\n")

        # --- Construcción y minimización del DFA ---
        f.write("afd_service  = AFDService()\n")
        f.write("tokens_norm  = normalize_regex(super_regex)\n")
        f.write("postfix      = parse_tokens(tokens_norm)\n")
        f.write("ast          = generate_ast(postfix)\n")
        f.write("dfa          = afd_service.build_dfa_from_ast(ast, token_names)\n")
        f.write("afd_service.minimize_dfa()\n\n")

        # --- entrypoint con filtrado ---
        f.write("def entrypoint(buffer: str):\n")
        f.write("    \"\"\"Escanea el buffer y devuelve lista de (token, lexeme),\n")
        f.write("       descartando espacios y comentarios.\"\"\"\n")
        f.write("    tokens = afd_service.scan_input(buffer)\n")
        f.write("    return [(tok,lex) for tok,lex in tokens\n")
        f.write("            if tok not in ('WHITESPACE','COMMENT')]\n\n")

        # --- Trailer del usuario ---
        if trailer:
            for line in trailer.splitlines():
                f.write(line.rstrip() + "\n")
            f.write("\n")

        # --- Modo standalone ---
        f.write("if __name__ == '__main__':\n")
        f.write("    import sys\n")
        f.write("    data = sys.stdin.read()\n")
        f.write("    for tok,lex in entrypoint(data):\n")
        f.write("        print(tok, lex)\n")
