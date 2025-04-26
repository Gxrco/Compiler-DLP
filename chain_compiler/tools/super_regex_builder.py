# chain_compiler/tools/super_regex_builder.py

import re

def clean_regex_part(regex):
    """
    Limpia y escapa correctamente una parte de expresión regular.
    - Reemplaza caracteres reales '\n', '\r', '\t' por sus secuencias literales.
    - Maneja literales entre comillas, clases y metacaracteres.
    """
    # 0) Convertir caracteres reales a secuencias
    regex = regex.replace('\n', r'\n').replace('\r', r'\r').replace('\t', r'\t')
    regex = regex.strip()

    metachar = r'{}[]().*+?^$|\\'

    # 1) Literales "..." o '...' con posible resto
    if regex and regex[0] in "\"'":
        quote = regex[0]
        end = regex.find(quote, 1)
        if end != -1:
            literal = regex[1:end]
            rest = regex[end+1:]
            return re.escape(literal) + rest

    # 2) Clase de caracteres al inicio, con posible resto
    if regex.startswith('['):
        close = regex.find(']')
        if close != -1:
            cls = regex[:close+1]
            rest = regex[close+1:]
            return cls + rest

    # 3) Metacaracter suelto
    if len(regex) == 1 and regex in metachar:
        return '\\' + regex

    # 4) Escapar metacaracteres individuales
    result = ''
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '\\' and i+1 < len(regex):
            result += regex[i:i+2]
            i += 2
        elif c in metachar:
            result += '\\' + c
            i += 1
        else:
            result += c
            i += 1

    # 5) Asegurar que no haya saltos de línea residuales
    return result.replace('\n', r'\n').replace('\r', r'\r')

def build_super_regex(rules):
    """
    Como antes, pero cada patrón ya viene sin líneas.
    """
    parts = []
    token_names = []

    for idx, (raw_regex, action) in enumerate(rules):
        pattern = raw_regex.strip()
        regex_clean = clean_regex_part(pattern)

        # Extraer nombre de token
        m = re.search(r'return\s+([A-Za-z_]\w*)', action)
        if m:
            token = m.group(1)
        elif 'raise' in action:
            token = 'EOF' if pattern.lower() == 'eof' else pattern.upper()
        else:
            token = 'UNKNOWN'
        token_names.append(token)

        marker = chr(1 + idx)
        parts.append(f"({regex_clean}){marker}")

    super_regex = "|".join(parts)
    print(f"Super-regex construido: {super_regex}")
    return super_regex, token_names
