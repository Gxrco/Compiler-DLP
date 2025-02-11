from regex_normalizer.tools.regex_parser import tokenize


def normalize_regex(regex):
    """
    Normaliza la expresión regular.
    
    Args:
        regex (str): La expresión regular de entrada.
    
    Returns:
        list: Lista de tokens normalizados.
    """
    tokens = tokenize(regex)
    return tokens

