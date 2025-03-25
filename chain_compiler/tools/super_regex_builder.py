def build_super_regex(rules):
    """
    Construye una super expresión regular a partir de una lista de reglas.
    
    Cada regla es una tupla (regex, action) donde 'action' contiene
    el token en formato, por ejemplo: return "TOKEN";
    
    La super expresión se genera combinando cada regla en el formato:
        (regex)#TOKEN
    y luego uniendo todas las reglas con el operador OR ('|').
    
    Args:
        rules (list of tuple(str, str)): Lista de reglas extraídas del archivo .yal
        
    Returns:
        str: La super expresión regular combinada
    """
    parts = []
    for regex, action in rules:
        try:
            # Extraer el token entre comillas en la acción
            token_match = action.strip().split('"')
            if len(token_match) >= 2:
                token = token_match[1].strip()
            else:
                # Si no hay comillas, intentar extraer el token de otra manera
                token = action.strip().split()[-1].rstrip(';')
                
            # Escapar caracteres especiales en el regex si es necesario
            # pero solo si no forman parte de una clase de caracteres o un operador
            
            # Formar la parte correspondiente a esta regla
            parts.append(f"({regex})#{token}")
        except IndexError:
            print(f"ADVERTENCIA: No se pudo extraer el token de la acción: {action}")
            # Usar un token genérico
            parts.append(f"({regex})#UNKNOWN")
    
    # Unir todas las partes con el operador OR
    super_regex = "|".join(parts)
    
    print(f"Super-regex construido: {super_regex}")
    return super_regex