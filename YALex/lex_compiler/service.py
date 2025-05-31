# YALEX/lex_compiler/service.py

from chain_compiler.tools.super_regex_builder import build_super_regex, DEFAULT_SENTINEL

def generate_lexer_py(yal_info: dict, output_path: str):
    """
    Genera un archivo .py que implemente el lexer definido en yal_info,
    usando el DFA interno para el escaneo.
    """
    header       = yal_info.get('header', '').strip()
    trailer      = yal_info.get('trailer', '').strip()
    alternatives = yal_info.get('alternatives', [])

    # Construimos super_regex con un sentinel que no existe en el input real:
    super_regex, token_names = build_super_regex(alternatives)

    with open(output_path, 'w', encoding='utf-8') as f:
        # --- Cabecera del usuario ---
        if header:
            f.write(header + "\n\n")

        # --- Cabecera del lexer: nombres y regex serializados con repr() ---
        f.write(f"token_names = {token_names!r}\n")
        f.write(f"super_regex = {super_regex!r}\n\n")

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

        # --- Definimos el mismo sentinel en el .py generado ---
        f.write(f"SENTINEL = {DEFAULT_SENTINEL!r}\n\n")

        # --- entrypoint con filtrado y sentinel fijo para el fin de token ---
        f.write("def entrypoint(buffer: str):\n")
        f.write("    \"\"\"Escanea el buffer y devuelve lista de (token, lexeme),\n")
        f.write("       descartando espacios, comentarios y errores léxicos.\"\"\"\n")
        f.write("    # agregamos el sentinel para delimitar el final\n")
        f.write("    tokens = afd_service.scan_input(buffer + SENTINEL)\n")
        # <<--- Aquí se añade 'ERROR' a la lista de tokens a filtrar --->
        f.write("    return [(tok, lex) for tok, lex in tokens\n")
        f.write("            if tok not in ('WHITESPACE','COMMENT','ERROR')]\n\n")

        # --- Trailer del usuario ---
        if trailer:
            for line in trailer.splitlines():
                f.write(line.rstrip() + "\n")
            f.write("\n")

        # --- Modo standalone ---
        f.write("if __name__ == '__main__':\n")
        f.write("    import sys\n")
        f.write("    data = sys.stdin.read()\n")
        f.write("    for tok, lex in entrypoint(data):\n")
        f.write("        print(tok, lex)\n")
