import re

def parse_yal_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return None

    result = {"header": "", "definitions": {}, "rules": [], "trailer": ""}

    # --- Extraer HEADER ---
    i = 0
    if lines and lines[0].strip() == "{":
        i += 1
        header_lines = []
        while i < len(lines) and lines[i].strip() != "}":
            header_lines.append(lines[i])
            i += 1
        result["header"] = "\n".join(header_lines).strip()
        i += 1

    # --- Extraer TRAILER ---
    j = len(lines) - 1
    if lines and lines[j].strip() == "}":
        j -= 1
        trailer_lines = []
        while j >= 0 and lines[j].strip() != "{":
            trailer_lines.append(lines[j])
            j -= 1
        result["trailer"] = "\n".join(reversed(trailer_lines)).strip()

    # --- Procesar DEFINICIONES y REGLAS entre header y trailer ---
    body = lines[i : j+1]
    raw_rules = []
    for line in body:
        line = line.strip()
        if not line or line.startswith("(*") or line.startswith("//"):
            continue
        if line.startswith("let"):
            m = re.match(r"let\s+(\w+)\s*=\s*(.+)", line)
            if m:
                result["definitions"][m.group(1)] = m.group(2).strip()
        else:
            m = re.match(r'^(.*?)\s*\{(.*)\}$', line)
            if m:
                raw_rules.append((m.group(1).strip(), m.group(2).strip()))

    # Expandir definiciones
    def expand(regex):
        if not result["definitions"]:
            return regex

        names = '|'.join(re.escape(k) for k in result["definitions"].keys())
        pattern = re.compile(r'(?:\{(' + names + r')\}|\b(' + names + r')\b)')

        while True:
            replaced = pattern.sub(lambda m: f'({result["definitions"][m.group(1) or m.group(2)]})', regex)
            if replaced == regex:
                break
            regex = replaced
        return regex

    for regex, action in raw_rules:
        result["rules"].append((expand(regex), action))

    return result