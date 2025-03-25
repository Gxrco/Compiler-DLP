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
        """
        Implementa correctamente el operador de diferencia (#) entre clases de caracteres.
        Convierte [a-z]#[aeiou] en una expresión que coincide con todas las letras excepto vocales.
        """
        pattern = re.compile(r'(\[[^\]]+\])\s*#\s*(\[[^\]]+\])')
        while True:
            m = pattern.search(regex)
            if not m:
                break

            def class_to_set(cls):
                """Convierte una clase de caracteres [a-z] en un conjunto de caracteres."""
                content = cls[1:-1]  # Quitar los corchetes
                # Verificar si es una clase negada
                is_negated = content.startswith('^')
                if is_negated:
                    content = content[1:]
                
                char_set = set()
                i = 0
                while i < len(content):
                    if i+2 < len(content) and content[i+1] == '-':
                        # Manejar rangos como 'a-z'
                        start_char, end_char = content[i], content[i+2]
                        for c in range(ord(start_char), ord(end_char) + 1):
                            char_set.add(chr(c))
                        i += 3
                    else:
                        # Carácter individual
                        char_set.add(content[i])
                        i += 1
                
                # Si la clase está negada, calcular el complemento
                if is_negated:
                    # Usamos un rango limitado de caracteres ASCII para el complemento
                    all_chars = set(chr(c) for c in range(32, 127))
                    char_set = all_chars - char_set
                
                return char_set

            left_set = class_to_set(m.group(1))
            right_set = class_to_set(m.group(2))
            diff_set = left_set - right_set
            
            if not diff_set:
                # Conjunto vacío, usar una expresión que nunca coincidirá
                replacement = "(?!.)"
            else:
                # Convertir el conjunto diferencia a una clase de caracteres
                # Para conjuntos pequeños, es más eficiente usar OR: (a|b|c)
                # Para conjuntos grandes, usar clase de caracteres: [abc]
                if len(diff_set) <= 5:
                    replacement = "(" + "|".join(sorted(diff_set)) + ")"
                else:
                    # Optimizar rangos contiguos para la clase de caracteres
                    chars_list = sorted(diff_set)
                    ranges = []
                    start = end = chars_list[0]
                    
                    for char in chars_list[1:]:
                        if ord(char) == ord(end) + 1:
                            end = char
                        else:
                            if start == end:
                                ranges.append(start)
                            else:
                                ranges.append(f"{start}-{end}")
                            start = end = char
                    
                    # Agregar el último rango
                    if start == end:
                        ranges.append(start)
                    else:
                        ranges.append(f"{start}-{end}")
                    
                    replacement = "[" + "".join(ranges) + "]"
            
            regex = regex[:m.start()] + replacement + regex[m.end():]
        
        return regex

    def strip_quotes(regex):
        """
        Elimina las comillas de los literales en la expresión regular.
        Convierte "token" en token, pero preserva el contenido entre comillas.
        """
        return re.sub(r'"([^"]*)"', r'\1', regex)

    # Procesar las reglas
    for regex, action in raw_rules:
        # Primero quitar comillas de literales
        regex = strip_quotes(regex)
        # Luego expandir las definiciones
        expanded = expand_defs(regex)
        # Corregir cualquier notación especial
        expanded = re.sub(r'\[\((.*?)\)\]', r'[\1]', expanded)
        # Aplicar operador de diferencia
        expanded = expand_difference(expanded)
        # Escapar caracteres especiales en literales que no son clases de caracteres
        # pero permitir que los metacaracteres de regex sigan funcionando
        result["rules"].append((expanded, action))

    return result