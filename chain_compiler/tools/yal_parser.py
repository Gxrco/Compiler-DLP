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
        header = []
        while i < len(lines) and lines[i].strip() != "}":
            header.append(lines[i])
            i += 1
        result["header"] = "\n".join(header).strip()
        i += 1

    # --- Extraer TRAILER ---
    j = len(lines) - 1
    if lines and lines[j].strip() == "}":
        j -= 1
        trailer = []
        while j >= 0 and lines[j].strip() != "{":
            trailer.append(lines[j])
            j -= 1
        result["trailer"] = "\n".join(reversed(trailer)).strip()

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

    def expand_defs(regex):
        if not result["definitions"]:
            return regex
        names = '|'.join(re.escape(k) for k in result["definitions"])
        # Captura tanto {NAME} como NAME (como palabra completa)
        pattern = re.compile(r'(?:\{(' + names + r')\}|\b(' + names + r')\b)')
        while True:
            replaced = pattern.sub(lambda m: f'({result["definitions"][m.group(1) or m.group(2)]})', regex)
            if replaced == regex:
                break
            regex = replaced
        return regex

    def expand_difference(regex):
        pattern = re.compile(r'(\[[^\]]+\])\s*#\s*(\[[^\]]+\])')
        while True:
            m = pattern.search(regex)
            if not m:
                break

            def class_to_set(cls):
                content = cls[1:-1]
                s = set()
                i = 0
                while i < len(content):
                    if i+2 < len(content) and content[i+1] == '-':
                        for c in range(ord(content[i]), ord(content[i+2]) + 1):
                            s.add(chr(c))
                        i += 3
                    else:
                        s.add(content[i])
                        i += 1
                return s

            left = class_to_set(m.group(1))
            right = class_to_set(m.group(2))
            diff = sorted(left - right)
            replacement = "(" + "|".join(diff) + ")"
            regex = regex[:m.start()] + replacement + regex[m.end():]
        return regex


    for regex, action in raw_rules:
        expanded = expand_defs(regex)
        expanded = re.sub(r'\[\((.*?)\)\]', r'[\1]', expanded)
        expanded = expand_difference(expanded)
        result["rules"].append((expanded, action))

    return result