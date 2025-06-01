# chain_compiler/tools/super_regex_builder.py

import re

# Un sentinel que NUNCA aparecerá en el input real:
DEFAULT_SENTINEL = '\x00'

def clean_regex_part(regex: str) -> str:
    """
    Limpia y escapa correctamente una parte de expresión regular.
    - Convierte saltos reales a '\\n', '\\r', '\\t'.
    - Deja intactos los character-classes completos.
    - Deja intactos los literales ya escapados.
    - Escapa el resto de metacaracteres sueltos.
    """
    # 0) Normalizar saltos y tabulaciones
    regex = regex.replace('\n', r'\n') \
                 .replace('\r', r'\r') \
                 .replace('\t', r'\t')
    regex = regex.strip()

    # 1) Si es una character-class completa, devolver tal cual
    if regex.startswith('[') and regex.endswith(']'):
        return regex

    # 2) Si ya viene escapada, devolver tal cual
    if regex.startswith('\\'):
        return regex

    # 3) Para literales entre comillas, no escapar
    if regex.startswith('"') and regex.endswith('"'):
        # Quitar las comillas y escapar el contenido
        inner = regex[1:-1]
        return re.escape(inner)

    # 4) Para todo lo demás, devolver sin modificar
    # (esto permite que las clases de caracteres funcionen correctamente)
    return regex

def build_super_regex(rules, sentinel: str = DEFAULT_SENTINEL):
    """
    Construye la super-regex concatenando cada patrón con su marcador
    y, al final, el sentinel como alternativa.
    """
    parts = []
    token_names = []

    for idx, (raw_regex, action) in enumerate(rules):
        pattern = raw_regex.strip()
        
        # Limpiar el patrón
        regex_clean = clean_regex_part(pattern)
        
        # Extraer nombre de token de la acción
        m = re.search(r'return\s+([A-Za-z_]\w*)', action)
        if m:
            token = m.group(1)
        else:
            token = 'UNKNOWN'
        token_names.append(token)

        # Marcador interno único para cada regla
        marker = chr(1 + idx)
        
        # Cada alternativa: (patrón)marcador
        # Importante: no agregar paréntesis extra si ya los tiene
        if regex_clean.startswith('(') and regex_clean.endswith(')'):
            parts.append(f"{regex_clean}{marker}")
        else:
            parts.append(f"({regex_clean}){marker}")

    # Agregar el sentinel al final
    parts.append(f"({re.escape(sentinel)})")

    # Unir todas las partes con |
    super_regex = "|".join(parts)
    
    # Debug: mostrar la super-regex construida
    print(f"Super-regex construida ({len(parts)} partes):")
    for i, part in enumerate(parts[:5]):
        print(f"  Parte {i}: {part}")
    if len(parts) > 5:
        print(f"  ... y {len(parts)-5} partes más")
    
    return super_regex, token_names