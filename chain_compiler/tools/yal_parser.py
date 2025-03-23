import re

def parse_yal_file(filepath):
    """
    Parsea un archivo .yal y separa las secciones:
    - header: bloque entre llaves { ... }
    - definitions: let NAME = regex
    - rules: regex { acción }
    - trailer: bloque entre llaves { ... }

    Retorna un diccionario con:
    - header: str
    - definitions: dict
    - rules: list de tuplas (regex, acción)
    - trailer: str
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return None

    result = {
        "header": "",
        "definitions": {},
        "rules": [],
        "trailer": ""
    }

    # Extraer bloques entre llaves { ... }
    blocks = re.findall(r'\{([^}]*)\}', content, re.DOTALL)
    remaining = re.sub(r'\{[^}]*\}', '', content, count=2, flags=re.DOTALL).strip()

    if len(blocks) >= 1:
        result["header"] = blocks[0].strip()
    if len(blocks) >= 2:
        result["trailer"] = blocks[-1].strip()

    # Procesar líneas restantes (definiciones y reglas)
    raw_rules = []
    for line in remaining.splitlines():
        line = line.strip()
        if not line or line.startswith('(*') or line.startswith('//'):
            continue
        if line.startswith("let"):
            # let ID = regex
            match = re.match(r"let\s+(\w+)\s*=\s*(.+)", line)
            if match:
                name, expr = match.group(1), match.group(2)
                result["definitions"][name] = expr.strip()
        else:
            match = re.match(r'(.+?)\s*\{(.*)\}', line)
            if match:
                regex = match.group(1).strip()
                action = match.group(2).strip()
                raw_rules.append((regex, action))

    # Expandir definiciones en las reglas
    def expand_definitions(regex, definitions):
        pattern = re.compile(r'\{(' + '|'.join(re.escape(k) for k in definitions.keys()) + r')\}')
        while True:
            replaced = pattern.sub(lambda m: f'({definitions[m.group(1)]})', regex)
            if replaced == regex:
                break
            regex = replaced
        return regex

    for regex, action in raw_rules:
        expanded_regex = expand_definitions(regex, result["definitions"])
        result["rules"].append((expanded_regex, action))

    return result
