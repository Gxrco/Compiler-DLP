# YALex/chain_compiler/tools/yal_parser.py

import re

def escape_string_literals(pat):
    """
    Sustituye cada "…" segmento en pat por su contenido escapado.
    """
    def repl(m):
        inner = m.group(1)
        # Convierte secuencias \n, \t… en su carácter real
        inner = bytes(inner, 'utf-8').decode('unicode_escape')
        # Escapa todo para regex
        return re.escape(inner)
    
    # Captura todo lo que esté entre dobles comillas
    return re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', repl, pat)

def remove_comments(text):
    """Elimina comentarios (* … *) del texto."""
    return re.sub(r'\(\*.*?\*\)', '', text, flags=re.DOTALL)

def parse_yal_file(filepath):
    """
    Parsea un archivo .yal y extrae las reglas de tokens.
    Retorna un diccionario con:
      - header: contenido del header
      - rule: nombre de la regla
      - alternatives: lista de (pattern, action)
      - trailer: contenido del trailer
    """
    with open(filepath, encoding='utf-8') as f:
        content = remove_comments(f.read())
    
    lines = content.splitlines()
    result = {"header": "", "rule": None, "alternatives": [], "trailer": ""}
    i = 0

    # --- Header ---
    while i < len(lines) and lines[i].strip() == "":
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

    # --- Rule ---
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    
    if i >= len(lines):
        raise ValueError("No se encontró declaración de regla.")
    
    # Buscar la línea que contiene "rule tokens ="
    rule_line = None
    while i < len(lines):
        if "rule tokens" in lines[i]:
            rule_line = lines[i].strip()
            break
        i += 1
    
    if not rule_line:
        raise ValueError("No se encontró 'rule tokens ='")
    
    # Extraer el nombre de la regla
    m = re.match(r'rule\s+(\w+)\s*=\s*(.*)', rule_line)
    if not m:
        raise ValueError(f"Línea inválida de regla: {rule_line}")
    
    result["rule"] = m.group(1)
    i += 1

    # --- Leer alternativas ---
    alts = []
    while i < len(lines):
        line = lines[i].strip()
        
        # Si encontramos un bloque de trailer, salir
        if line.startswith("{") and "return" not in line:
            break
        
        # Si la línea no está vacía, es una alternativa
        if line:
            alts.append(line)
        i += 1

    # Procesar las alternativas
    for alt_line in alts:
        # Quitar el | inicial si existe
        if alt_line.startswith("|"):
            alt_line = alt_line[1:].strip()
        
        # Buscar el patrón y la acción
        # El patrón termina donde empieza { return ... }
        brace_pos = alt_line.find("{")
        if brace_pos == -1:
            continue
        
        pattern = alt_line[:brace_pos].strip()
        
        # Extraer la acción entre { }
        action_start = brace_pos + 1
        action_end = alt_line.rfind("}")
        if action_end == -1:
            continue
        
        action = alt_line[action_start:action_end].strip()
        
        # Procesar el patrón
        # Si es un literal entre comillas, extraerlo y escaparlo
        if pattern.startswith('"') and pattern.endswith('"'):
            inner = pattern[1:-1]
            # Decodificar secuencias de escape
            try:
                inner = bytes(inner, "utf-8").decode("unicode_escape")
            except:
                pass
            # Escapar para regex
            processed_pattern = re.escape(inner)
        else:
            # Para otros patrones (como clases de caracteres), dejar tal cual
            processed_pattern = pattern
        
        result["alternatives"].append((processed_pattern, action))

    # --- Trailer ---
    while i < len(lines):
        if lines[i].lstrip().startswith("{"):
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
            break
        i += 1

    return result