# chain_compiler/tools/super_regex_builder.py

import re

# Un sentinel que NUNCA aparecerá en el input real:
DEFAULT_SENTINEL = '\x00'

def clean_regex_part(regex: str) -> str:
    """
    Limpia y escapa correctamente una parte de expresión regular.
    - Convierte saltos reales a '\\n', '\\r', '\\t'.
    - Deja intactos los character-classes completos al inicio.
    - Deja intactos los literales ya escapados (p.ej. '\\+' o '\\-').
    - Escapa el resto de metacaracteres sueltos.
    """
    # 0) Normalizar saltos y tabulaciones
    regex = regex.replace('\n', r'\n') \
                 .replace('\r', r'\r') \
                 .replace('\t', r'\t')
    regex = regex.strip()

    # 1) Si empieza con una character-class, la conservamos entera:
    if regex.startswith('['):
        close = regex.find(']')
        if close != -1:
            cls = regex[:close+1]
            rest = regex[close+1:]
            return cls + rest

    # 2) Si ya viene escapada al principio, devolvemos tal cual:
    if regex.startswith('\\'):
        return regex

    # 3) Para todo lo demás, escapamos los metacaracteres básicos:
    metachar = r'{}[]().*+?^$|\\'
    result = ''
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '\\' and i+1 < len(regex):
            # preservamos la pareja de escape completa
            result += regex[i:i+2]
            i += 2
        elif c in metachar:
            result += '\\' + c
            i += 1
        else:
            result += c
            i += 1

    return result

def build_super_regex(rules, sentinel: str = DEFAULT_SENTINEL):
    """
    Construye la super-regex concatenando cada patrón (con su marcador)
    y, al final, el sentinel como alternativa.
    Devuelve (super_regex, token_names).
    """
    parts = []
    token_names = []

    for idx, (raw_regex, action) in enumerate(rules):
        pattern     = raw_regex.strip()
        regex_clean = clean_regex_part(pattern)
        # colapsar espacios contiguos (solo en la parte textual)
        regex_clean = re.sub(r'\s+', ' ', regex_clean)

        # extraer nombre de token de la acción:
        m = re.search(r'return\s+([A-Za-z_]\w*)', action)
        if m:
            token = m.group(1)
        elif 'raise' in action:
            token = 'EOF' if pattern.lower() == 'eof' else pattern.upper()
        else:
            token = 'UNKNOWN'
        token_names.append(token)

        # marcador interno (Chr(1), Chr(2), …)
        marker = chr(1 + idx)
        # cada alternativa: (patrón)marcador
        parts.append(f"({regex_clean}){marker}")

    # por último, la alternativa sentinel (sin marcador, no genera token)
    parts.append(f"({re.escape(sentinel)})")

    super_regex = "|".join(parts)
    print(f"Super-regex construido: {super_regex}")
    return super_regex, token_names