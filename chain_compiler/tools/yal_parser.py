import re

def remove_comments(text):
    """
    Elimina comentarios en el formato (* ... *) de todo el texto.
    """
    return re.sub(r'\(\*.*?\*\)', '', text, flags=re.DOTALL)

def parse_yal_file(filepath):
    """
    Parsea un archivo YAL que siga el formato definido.
    Versión robusta que maneja correctamente caracteres especiales.
    
    Args:
        filepath (str): Ruta al archivo YAL
        
    Returns:
        dict: Diccionario con la información extraída del archivo
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return None

    # Elimina comentarios
    content = re.sub(r'\(\*.*?\*\)', '', content, flags=re.DOTALL)
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

    # Procesar bloque Header si existe
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

    # Recoger las líneas que contienen las alternativas
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
    
    # Usando una expresión regular más robusta para manejar el separador '|'
    # que no esté dentro de clases de caracteres o escapado
    def split_by_unescaped_pipe(text):
        parts = []
        current = ""
        in_class = 0
        escaped = False
        
        for char in text:
            if escaped:
                current += char
                escaped = False
            elif char == '\\':
                current += char
                escaped = True
            elif char == '[':
                current += char
                in_class += 1
            elif char == ']' and in_class > 0:
                current += char
                in_class -= 1
            elif char == '|' and in_class == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        
        if current:
            parts.append(current.strip())
        
        return parts
    
    alt_parts = split_by_unescaped_pipe(alternatives_str)

    # Procesar cada alternativa
    for alt in alt_parts:
        # Usar una expresión regular robusta para capturar patrón y acción
        # que manejen correctamente las llaves anidadas
        def match_pattern_and_action(text):
            """
            Encuentra un patrón y su acción, manejando correctamente llaves anidadas.
            """
            pattern = ""
            action = ""
            i = 0
            while i < len(text) and text[i] != '{':
                pattern += text[i]
                i += 1
            
            if i >= len(text):
                return None, None
            
            # Ahora estamos en '{'
            brace_depth = 1
            i += 1  # Saltar '{'
            while i < len(text) and brace_depth > 0:
                if text[i] == '{':
                    brace_depth += 1
                elif text[i] == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        break
                action += text[i]
                i += 1
            
            if brace_depth != 0:
                return None, None
            
            # Eliminar comentarios al final
            remaining = text[i+1:].strip()
            if remaining.startswith('#'):
                # Es un comentario, ignorarlo
                pass
                
            return pattern.strip(), action.strip()
        
        pattern, action = match_pattern_and_action(alt)
        if pattern is not None and action is not None:
            # Manejar casos especiales para las llaves
            if pattern in [r"\{", "\\{", r"\x7B"]:
                pattern = "{"
            elif pattern in [r"\}", "\\}", r"\x7D"]:
                pattern = "}"
                
            result["alternatives"].append((pattern, action))
        else:
            print(f"Línea ignorada o con formato inválido en alternativas: {alt}")
    
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

    # Para mayor robustez, asegurarse de que las llaves estén incluidas
    # si no se encontraron en las alternativas
    has_lbrace = any(pattern in ["{", "\\{", "\x7B"] for pattern, _ in result["alternatives"])
    has_rbrace = any(pattern in ["}", "\\}", "\x7D"] for pattern, _ in result["alternatives"])
    
    if not has_lbrace:
        result["alternatives"].append(("{", "return LBRACE"))
    if not has_rbrace:
        result["alternatives"].append(("}", "return RBRACE"))

    return result