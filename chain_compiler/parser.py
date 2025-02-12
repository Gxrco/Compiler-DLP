from chain_compiler.tools.shunting_yard import convert_to_postfix

def parse_tokens(tokens):
    """
    Convierte la lista de tokens en notación infix a notación postfix.

    Args:
        tokens (list): Lista de tokens en notación infix.

    Returns:
        list: Lista de tokens en notación postfix.
    """
    postfix_tokens = convert_to_postfix(tokens)
    return postfix_tokens


