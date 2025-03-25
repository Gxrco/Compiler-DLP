import re

def clean_regex_part(regex):
    """
    Limpia y escapa correctamente una parte de expresión regular.
    Maneja de forma especial los caracteres con significado especial en RegEx.
    
    Args:
        regex (str): La expresión regular a limpiar
        
    Returns:
        str: La expresión regular limpia y correctamente escapada
    """
    regex = regex.strip()
    
    # Casos especiales para llaves y otros caracteres metacaracteres
    metacharacters = r'{}[]().*+?^$|\\'
    
    # Si es un solo carácter especial
    if len(regex) == 1 and regex in metacharacters:
        return f'\\{regex}'
    
    # Si está entre comillas, quitar las comillas
    if (regex.startswith('"') and regex.endswith('"')) or (regex.startswith("'") and regex.endswith("'")):
        if len(regex) > 2:
            regex = regex[1:-1]
    
    # Si es una clase de caracteres, conservarla tal cual
    if regex.startswith('[') and regex.endswith(']'):
        return regex
    
    # Para otros casos, escapar solo los metacaracteres no escapados
    result = ""
    i = 0
    while i < len(regex):
        if regex[i] == '\\' and i + 1 < len(regex):
            # Ya está escapado, conservar como está
            result += regex[i:i+2]
            i += 2
        elif regex[i] in metacharacters:
            # Escapar metacaracteres
            result += '\\' + regex[i]
            i += 1
        else:
            # Caracteres normales
            result += regex[i]
            i += 1
    
    return result

def build_super_regex(rules):
    """
    Construye una super expresión regular a partir de una lista de reglas.
    Versión robusta que maneja caracteres especiales.
    
    Args:
        rules (list): Lista de tuplas (regex, action)
        
    Returns:
        str: La super expresión regular
    """
    parts = []
    
    # Procesar cada regla
    for regex, action in rules:
        # Casos especiales para caracteres problemáticos
        if regex == "{":
            regex_clean = "\\{"
        elif regex == "}":
            regex_clean = "\\}"
        else:
            # Limpia la parte de la regex para remover comillas y escapar metacaracteres
            regex_clean = clean_regex_part(regex.strip())
        
        # Extrae el token de la acción
        token = "UNKNOWN"
        action = action.strip()
        
        # Intentar extraer el token si la acción usa return
        m = re.search(r'return\s+([A-Za-z_]\w*)', action)
        if m:
            token = m.group(1)
        elif "raise" in action:
            if regex.strip() == "eof":
                token = "EOF"
            else:
                token = regex.strip().upper()
        
        parts.append(f"({regex_clean})#{token}")
    
    super_regex = "|".join(parts)
    print(f"Super-regex construido: {super_regex}")
    return super_regex