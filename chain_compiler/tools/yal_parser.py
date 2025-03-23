import re

def parse_yal_file(filepath):
    """
    Parsea un archivo .yal y separa las secciones:
    - header: bloque entre las primeras llaves { ... }
    - definitions: líneas con let NAME = regex
    - rules: regex { acción }
    - trailer: bloque entre las últimas llaves { ... }

    Retorna un diccionario con las secciones.
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return None

    result = {
        "header": "",
        "definitions": [],
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
    for line in remaining.splitlines():
        line = line.strip()
        if not line or line.startswith('(*') or line.startswith('//'):
            continue
        if line.startswith("let"):
            result["definitions"].append(line)
        else:
            match = re.match(r'(.+?)\s*\{(.*)\}', line)
            if match:
                regex = match.group(1).strip()
                action = match.group(2).strip()
                result["rules"].append((regex, action))

    return result
