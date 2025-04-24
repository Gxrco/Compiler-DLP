from chain_compiler.tools.super_regex_builder import build_super_regex

def generate_lexer_py(yal_info: dict, output_path: str):
    """
    Genera un archivo Python que implemente el lexer definido en yal_info,
    usando el DFA interno para el escaneo.

    Args:
        yal_info (dict): Contiene 'header', 'alternatives', 'trailer'.
        output_path (str): Ruta del archivo .py de salida.
    """
    header      = yal_info.get('header', '').strip()
    trailer     = yal_info.get('trailer', '').strip()
    alternatives = yal_info.get('alternatives', [])

    # 1) Generar super-regex (solo para el DFA; descartamos token_names aquí)
    super_regex, _ = build_super_regex(alternatives)

    with open(output_path, 'w', encoding='utf-8') as f:
        # -- Cabecera del usuario --
        if header:
            f.write(header + "\n\n")

        # -- Importaciones de las librerías internas --
        f.write("from chain_compiler.normalizer import normalize_regex\n")
        f.write("from chain_compiler.parser import parse_tokens\n")
        f.write("from chain_compiler.ast_service import generate_ast\n")
        f.write("from afd_compiler.service import AFDService\n\n")

        # -- Construcción del DFA en tiempo de carga --
        f.write("# Configurar y minimizar el DFA\n")
        f.write("afd_service = AFDService()\n")
        f.write("tokens_norm = normalize_regex(r'''" + super_regex + "''')\n")
        f.write("postfix     = parse_tokens(tokens_norm)\n")
        f.write("ast         = generate_ast(postfix)\n")
        f.write("dfa         = afd_service.build_dfa_from_ast(ast)\n")
        f.write("afd_service.minimize_dfa()\n\n")

        # -- Función entrypoint: retorno directo de scan_input --
        f.write("def entrypoint(buffer: str):\n")
        f.write("    '''Escanea el buffer y devuelve lista de (token, lexeme)'''\n")
        f.write("    return afd_service.scan_input(buffer)\n\n")

        # -- Trailer del usuario, línea a línea --
        if trailer:
            for line in trailer.splitlines():
                f.write(line.rstrip() + "\n")
            f.write("\n")

        # -- Modo standalone: leer stdin y tokenizar --
        f.write("if __name__ == '__main__':\n")
        f.write("    import sys\n")
        f.write("    data = sys.stdin.read()\n")
        f.write("    for tok, lex in entrypoint(data):\n")
        f.write("        print(tok, lex)\n")
