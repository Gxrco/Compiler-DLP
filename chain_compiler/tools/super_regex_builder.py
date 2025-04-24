import re

def clean_regex_part(regex):
    """
    Limpia y escapa correctamente una parte de expresión regular.
    Maneja:
      - Literales entre comillas "..." o '...' seguidos de clases/cuántificadores.
      - Clases de caracteres [..] opcionalmente con +*? tras el cierre.
      - Metacaracteres sueltos.
    """
    regex = regex.strip()
    metachar = r'{}[]().*+?^$|\\'

    # 1) Literal entre comillas, con posible resto
    if regex and regex[0] in "'\"":
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
    return result


def remove_space_outside_classes(s: str) -> str:
    """
    Elimina espacios que no estén dentro de clases de caracteres '[...]'.
    """
    out = []
    in_cls = False
    for ch in s:
        if ch == '[':
            in_cls = True
            out.append(ch)
        elif ch == ']':
            in_cls = False
            out.append(ch)
        elif ch == ' ' and not in_cls:
            continue
        else:
            out.append(ch)
    return ''.join(out)


def build_super_regex(rules):
    """
    Construye una super-expresión regular a partir de una lista de reglas YAL,
    asignando a cada alternativa un marcador único y devolviendo también
    la lista de nombres de token en orden.

    Args:
        rules (list of (regex, action) tuples)
    Returns:
        tuple: (super_regex: str, token_names: list of str)
    """
    parts = []
    token_names = []

    for idx, (raw_regex, action) in enumerate(rules):
        # Quitar espacios alrededor de la definición
        pattern = raw_regex.strip()
        # Limpiar el patrón
        regex_clean = clean_regex_part(pattern)
        # Eliminar espacios sueltos fuera de las clases
        regex_clean = remove_space_outside_classes(regex_clean)

        # Extraer nombre de token
        m = re.search(r'return\s+([A-Za-z_]\w*)', action)
        if m:
            token = m.group(1)
        elif 'raise' in action:
            token = 'EOF' if pattern.lower() == 'eof' else pattern.upper()
        else:
            token = 'UNKNOWN'
        token_names.append(token)

        # Marcador único (chr(1), chr(2), …)
        marker = chr(1 + idx)
        parts.append(f"({regex_clean}){marker}")

    super_regex = '|'.join(parts)
    print(f"Super-regex construido: {super_regex}")
    return super_regex, token_names
