import re

def remove_comments(text):
    """
    Elimina comentarios en el formato (* ... *) de todo el texto.
    """
    return re.sub(r'\(\*.*?\*\)', '', text, flags=re.DOTALL)

def parse_yal_file(filepath):
    """
    Parsea un archivo YAL que siga el siguiente formato:
    
    (* comentarios opcionales *)
    {
      ... código de header ...
    }
    rule <nombre_regla> =
      <regex1> { <acción1> }
    | <regex2> { <acción2> }
    | ...
    [| ...]
    [opcional bloque trailer:
    {
      ... código de trailer ...
    }]
    
    Retorna un diccionario con:
      - header: código del bloque header (opcional)
      - rule: nombre de la regla principal
      - alternatives: lista de tuplas (regex, acción)
      - trailer: código del bloque trailer (opcional)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return None

    # Elimina comentarios
    content = remove_comments(content)
    lines = content.splitlines()

    result = {
        "header": "",
        "rule": None,
        "alternatives": [],
        "trailer": ""
    }

    i = 0
    # Saltar líneas en blanco
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Procesar bloque Header si existe (se asume que empieza con '{')
    if i < len(lines) and lines[i].strip().startswith("{"):
        header_lines = []
        line = lines[i].strip()
        # Si la línea contiene ambas llaves en la misma línea
        if line.endswith("}"):
            header_lines.append(line[1:-1].strip())
            i += 1
        else:
            header_lines.append(line[1:].strip())
            i += 1
            while i < len(lines) and "}" not in lines[i]:
                header_lines.append(lines[i].strip())
                i += 1
            if i < len(lines):
                header_line = lines[i].strip()
                idx = header_line.find("}")
                header_lines.append(header_line[:idx].strip())
                i += 1
        result["header"] = "\n".join(header_lines).strip()

    # Saltar líneas en blanco hasta encontrar la declaración de regla
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Procesar la línea de declaración de la regla: "rule <nombre> ="
    if i < len(lines):
        rule_line = lines[i].strip()
        m_rule = re.match(r'rule\s+(\w+)\s*=\s*(.*)', rule_line)
        if m_rule:
            result["rule"] = m_rule.group(1)
            # Si hay contenido en la misma línea después de "=" se toma como parte de las alternativas
            alternatives_text = m_rule.group(2).strip()
            i += 1
        else:
            print("No se encontró la declaración de regla en la línea:", rule_line)
            return None
    else:
        print("Archivo vacío o sin declaración de regla.")
        return None

    # Recoger las líneas que contienen las alternativas (hasta llegar a un bloque trailer o al fin del archivo)
    alt_lines = []
    if alternatives_text:
        alt_lines.append(alternatives_text)
    while i < len(lines):
        line = lines[i].strip()
        # Si detectamos un bloque trailer, dejamos de procesar alternativas
        if line.startswith("{"):
            break
        if line != "":
            alt_lines.append(line)
        i += 1

    # Unir las líneas de alternativas y dividir por el separador '|'
    alternatives_str = " ".join(alt_lines)
    alt_parts = [part.strip() for part in alternatives_str.split("|") if part.strip()]

    # Cada alternativa debe tener el formato: <regex> { <acción> }
    for alt in alt_parts:
        m_alt = re.match(r'(.+?)\s*\{\s*(.+?)\s*\}\s*$', alt)
        if m_alt:
            regex_part = m_alt.group(1).strip()
            action_part = m_alt.group(2).strip()
            result["alternatives"].append((regex_part, action_part))
        else:
            print("Línea ignorada o con formato inválido en alternativas:", alt)
    
    # Procesar bloque Trailer si existe
    if i < len(lines) and lines[i].strip().startswith("{"):
        trailer_lines = []
        line = lines[i].strip()
        if line.endswith("}"):
            trailer_lines.append(line[1:-1].strip())
            i += 1
        else:
            trailer_lines.append(line[1:].strip())
            i += 1
            while i < len(lines) and "}" not in lines[i]:
                trailer_lines.append(lines[i].strip())
                i += 1
            if i < len(lines):
                trailer_line = lines[i].strip()
                idx = trailer_line.find("}")
                trailer_lines.append(trailer_line[:idx].strip())
                i += 1
        result["trailer"] = "\n".join(trailer_lines).strip()

    return result
