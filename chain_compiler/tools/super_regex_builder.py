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
            # Se asume que la acción tiene el token entre comillas, por ejemplo: return "CONS";
            token = action.split('"')[1]
        except IndexError:
            raise ValueError(f"Acción mal formada: {action}")
        parts.append(f"({regex})#{token}")
    super_regex = "|".join(parts)
    return super_regex

# Prueba interna (opcional)
if __name__ == '__main__':
    # Ejemplo de uso:
    sample_rules = [
        ("[a-z]#[aeiou]+", 'return "CONS";'),
        ("[aeiou]+", 'return "VOC";'),
        ("[0-9]+", 'return "NUM";'),
        ('"="', 'return "IGUAL";')
    ]
    print("Super-regex combinado:", build_super_regex(sample_rules))
