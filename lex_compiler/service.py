'''
Generador de código Python para el analizador léxico basado en YALex,
utilizando las librerías internas para construir el AFD en tiempo de carga
'''

def generate_lexer_py(yal_info: dict, output_path: str):
    """
    Genera un archivo Python que implemente el lexer definido en yal_info,
    usando las librerías internas de cadena y AFD.

    Args:
        yal_info (dict): Contiene 'header', 'alternatives' (lista de tuplas (pattern, action)), 'trailer'.
        output_path (str): Ruta del archivo .py de salida.
    """
    header = yal_info.get('header', '').strip()
    trailer = yal_info.get('trailer', '').strip()
    alternatives = yal_info.get('alternatives', [])

    # Construir la super-regex en tiempo de generación
    from chain_compiler.tools.super_regex_builder import build_super_regex
    super_regex = build_super_regex(alternatives)

    with open(output_path, 'w', encoding='utf-8') as f:
        # 1. Escribir header del usuario
        if header:
            f.write(header + "\n\n")

        # 2. Importaciones de las librerías internas
        f.write("from chain_compiler.normalizer import normalize_regex\n")
        f.write("from chain_compiler.parser import parse_tokens\n")
        f.write("from chain_compiler.ast_service import generate_ast\n")
        f.write("from afd_compiler.service import AFDService\n\n")

        # 3. Incluir literal de la super-regex
        f.write(f"# Super-regex construido en generación\n")
        f.write(f"super_regex = r'''{super_regex}'''\n\n")

        # 4. Construir y minimizar el DFA al importar el módulo
        f.write("# Inicialización del AFD en tiempo de carga\n")
        f.write("afd_service = AFDService()\n")
        f.write("tokens_norm = normalize_regex(super_regex)\n")
        f.write("postfix = parse_tokens(tokens_norm)\n")
        f.write("ast = generate_ast(postfix)\n")
        f.write("dfa = afd_service.build_dfa_from_ast(ast)\n")
        f.write("afd_service.minimize_dfa()\n\n")

        # 5. Función entrypoint usando el AFD interno
        f.write("def entrypoint(buffer: str):\n")
        f.write("    '''Escanea el buffer y devuelve lista de (token, lexeme) usando el DFA interno'''\n")
        f.write("    return afd_service.scan_input(buffer)\n\n")

        # 6. Escribir trailer del usuario
        if trailer:
            f.write(trailer + "\n\n")

        # 7. Standalone: leer de stdin y ejecutar entrypoint
        f.write("if __name__ == '__main__':\n")
        f.write("    import sys\n")
        f.write("    data = sys.stdin.read()\n")
        f.write("    for tok, lex in entrypoint(data):\n")
        f.write("        print(tok, lex)\n")
