# chain_compiler/tools/super_regex_builder.py

import re

# Marcador que nunca aparece en un programa “real”:
DEFAULT_SENTINEL = '\x00'

def clean_regex_part(raw: str) -> str:
    """
    Toma la “raw pattern” que viene desde el .yal y la regresa lista para concatenar:
      1) Si es exactamente "\"if\"" (literal entre comillas), quita las comillas y escapa el contenido: re.escape(inner).
      2) Si es "\n", "\r\n" o "\t" *exactamente*, devuelve '\\n', '\\r\\n' o '\\t' (para que el parser de regex los vea como literales).
      3) Si es una character‐class completa (p.ej. "[a-z]"), la deja tal cual.
      4) Si empieza con '\\' (p.ej. "\\."), la deja tal cual.
      5) En cualquier otro caso (p.ej. "<", ">", “>=", etc.), devuelve la cadena sin modificar,
         para que luego la envolvamos en paréntesis al armar el OR final.
    """
    s = raw.strip()

    # 1) Si está entre comillas dobles EXACTAS, quito comillas y escapo el interior:
    if s.startswith('"') and s.endswith('"'):
        inner = s[1:-1]
        # p. ej. raw='"if"' → inner="if" → re.escape(inner)="if"
        return re.escape(inner)

    # 2) Si la cadena es textualmente "\n", "\r\n" o "\t" → la devolvemos escapada:
    if s == r'\n':
        return r'\n'
    if s == r'\r\n':
        return r'\r\n'
    if s == r'\t':
        return r'\t'

    # 3) Si es una character‐class completa (empieza con [ y termina con ]), la dejamos intacta:
    if s.startswith('[') and s.endswith(']'):
        return s

    # 4) Si ya viene escapada (por ejemplo "\."), la dejamos intacta:
    if s.startswith('\\'):
        return s

    # 5) Caso normal (por ej. "<" o ">="), devolvemos sin modificar para luego encerrarla en ().
    return s



def build_super_regex(rules, sentinel: str = DEFAULT_SENTINEL):
    """
    Cada elemento de `rules` es (raw_pattern, action_string). Queremos:
      1) Limpiar raw_pattern con clean_regex_part().
      2) Extraer nombre de token (p.ej. “IF”, “ID”, etc.) de action_string.
      3) Construir una lista “parts” donde cada elemento sea "(patrón)⌕" 
         (⌕ = chr(1 + índice) es el marcador único de esa regla).
      4) Al final, añadir la rama "(\\x00)" para el sentinel.

    El OR resultante debe *respetar* el orden exacto en que aparecen las líneas
    dentro de ejemplo3.yal, de arriba hacia abajo.
    """
    parts       = []
    token_names = []

    for idx, (raw_pattern, action) in enumerate(rules):
        cleaned = clean_regex_part(raw_pattern)

        #  Extraer “return XXX” de la acción para saber el nombre de token:
        m = re.search(r'return\s+([A-Za-z_]\w*)', action)
        tok = m.group(1) if m else 'UNKNOWN'
        token_names.append(tok)

        marker = chr(1 + idx)   # chr(1), chr(2), ... chr(N)

        # Lo envolvemos en paréntesis para que no cambie la precedencia:
        # Ejemplo: si cleaned = "if", ponemos "(if)\x02".
        parts.append(f"({cleaned}){marker}")

    # Finalmente, agrego la alternativa que solo es el sentinel:
    parts.append(f"({re.escape(sentinel)})")

    # Uno todo con '|' en el mismo orden en que estoy recorriendo `rules`.
    super_regex = "|".join(parts)
    return super_regex, token_names
