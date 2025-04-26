# parser_yal.py

import re

def escape_string_literals(pat):
    """
    Sustituye cada "…"-segmento en pat por su contenido escapado
    (resolviendo \n, \t, etc. antes de hacer re.escape).
    Ejemplo: '"#"[^\\n]*' → '#[^\\n]*'
    """
    def repl(m):
        inner = m.group(1)
        # convierte secuencias \n, \t… en su caracter real
        inner = bytes(inner, 'utf-8').decode('unicode_escape')
        # escapa todo para regex
        return re.escape(inner)
    # captura todo lo que esté entre dobles comillas,
    # permitiendo \" en medio
    return re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', repl, pat)

def remove_comments(text):
    """Elimina comentarios (* … *) del texto."""
    return re.sub(r'\(\*.*?\*\)', '', text, flags=re.DOTALL)

def parse_yal_file(filepath):
    """
    Parsea un archivo .yal, devolviendo:
      header      : contenido opcional antes de 'rule'
      rule        : nombre de la regla
      alternatives: lista de (pattern, action)
      trailer     : contenido opcional después de las alternativas
    Preserva indentación en header/trailer.
    """
    with open(filepath, encoding='utf-8') as f:
        content = remove_comments(f.read())
    lines = content.splitlines()
    result = {"header":"", "rule":None, "alternatives":[], "trailer":""}
    i = 0

    # ——— Header ———
    while i < len(lines) and lines[i].strip()=="":
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("{"):
        hdr = []
        if "}" in lines[i]:
            line = lines[i]
            hdr.append(line[line.find("{")+1 : line.find("}")])
            i += 1
        else:
            hdr.append(lines[i][lines[i].find("{")+1:])
            i += 1
            while i < len(lines) and "}" not in lines[i]:
                hdr.append(lines[i])
                i += 1
            if i < len(lines):
                line = lines[i]
                hdr.append(line[:line.find("}")])
                i += 1
        result["header"] = "\n".join(hdr)

    # ——— Regla ———
    while i < len(lines) and lines[i].strip()=="":
        i += 1
    if i >= len(lines):
        raise ValueError("Sin declaración de regla.")
    m = re.match(r'rule\s+(\w+)\s*=\s*(.*)', lines[i].strip())
    if not m:
        raise ValueError(f"Línea inválida de regla: {lines[i]}")
    result["rule"] = m.group(1)
    alt_text = m.group(2).strip()
    i += 1

    # ——— Leer alternativas ———
    alts = [alt_text] if alt_text else []
    while i < len(lines) and not lines[i].lstrip().startswith("{"):
        if lines[i].strip():
            alts.append(lines[i].strip())
        i += 1

    def split_unescaped(text):
        parts, cur = [], ""
        in_class = esc = False
        for ch in text:
            if esc:
                cur += ch; esc = False
            elif ch == "\\":
                cur += ch; esc = True
            elif ch == "[":
                cur += ch; in_class = True
            elif ch == "]" and in_class:
                cur += ch; in_class = False
            elif ch == "|" and not in_class:
                parts.append(cur.strip()); cur = ""
            else:
                cur += ch
        if cur:
            parts.append(cur.strip())
        return parts

    for alt in split_unescaped(" ".join(alts)):
        line = alt.lstrip()
        if line.startswith("|"):
            line = line[1:].lstrip()

        # buscar '{' real (fuera de comillas y clases)
        brace = None
        in_q = in_c = esc = False
        for j,ch in enumerate(line):
            if esc:
                esc = False; continue
            if ch == "\\":
                esc = True; continue
            if ch == '"' and not in_c:
                in_q = not in_q; continue
            if ch == "[" and not in_q:
                in_c = True; continue
            if ch == "]" and in_c:
                in_c = False; continue
            if ch == "{" and not in_q and not in_c:
                brace = j
                break
        if brace is None:
            continue

        pat = line[:brace].strip()
        # desempaquetar literales completos
        if pat.startswith('"') and pat.endswith('"'):
            inner = pat[1:-1]
            inner = bytes(inner, "utf-8").decode("unicode_escape")
            pat = re.escape(inner)
        else:
            # reemplazar cualquier fragmento "..." en medio
            pat = escape_string_literals(pat)

        # extraer acción
        rest = line[brace:]
        act = ""
        depth = 0
        for ch in rest:
            if ch == "{":
                depth += 1
                continue
            if ch == "}":
                depth -= 1
                if depth == 0:
                    break
                act += ch
            elif depth >= 1:
                act += ch

        result["alternatives"].append((pat, act.strip()))

    # ——— Trailer ———
    if i < len(lines) and lines[i].lstrip().startswith("{"):
        tr = []
        if "}" in lines[i]:
            line = lines[i]
            tr.append(line[line.find("{")+1 : line.find("}")])
            i += 1
        else:
            tr.append(lines[i][lines[i].find("{")+1:])
            i += 1
            while i < len(lines) and "}" not in lines[i]:
                tr.append(lines[i])
                i += 1
            if i < len(lines):
                line = lines[i]
                tr.append(line[:line.find("}")])
                i += 1
        result["trailer"] = "\n".join(tr)

    return result
