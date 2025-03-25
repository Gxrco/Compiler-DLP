import re

def clean_regex_part(regex):
    """
    Limpia la parte de la expresión regular removiendo comillas innecesarias
    y, en el caso de literales simples que sean metacaracteres, los escapa.
    
    Ejemplos:
      "['0'-'9']+" -> "[0-9]+"
      "[' ' '\t']" -> "[ \t]"
      "'+'"        -> "\+"
    """
    regex = regex.strip()
    # Si se trata de una clase de caracteres, remueve las comillas internas.
    if regex.startswith('[') and ']' in regex:
        def remove_quotes_in_class(match):
            content = match.group(1)
            # Remover todas las comillas simples
            return "[" + content.replace("'", "") + "]"
        regex = re.sub(r'\[([^\]]+)\]', remove_quotes_in_class, regex)
    else:
        # Si está entre comillas, se remueven
        if regex.startswith("'") and regex.endswith("'"):
            regex = regex[1:-1]
        # Si es un solo carácter y es un metacarácter, se escapa
        if len(regex) == 1 and regex in "+*?()|.^$-":
            regex = "\\" + regex
    return regex

def build_super_regex(rules):
    """
    Construye una super expresión regular a partir de una lista de reglas.
    
    Cada regla es una tupla (regex, action) donde 'action' contiene la acción asociada.
    Se genera combinando cada regla en el formato:
        (regex)#TOKEN
    y luego uniendo todas las reglas con el operador OR ('|').
    """
    parts = []
    for regex, action in rules:
        # Limpia la parte de la regex para remover comillas innecesarias y escapar literales.
        regex_clean = clean_regex_part(regex.strip())
        token = "UNKNOWN"
        action = action.strip()
        # Intentar extraer el token si la acción usa return con comillas
        m = re.search(r'return\s+[\'"]([^\'"]+)[\'"]', action)
        if m:
            token = m.group(1)
        elif "raise" in action:
            # Si es raise y la regex es "eof", asignamos EOF
            if regex.strip() == "eof":
                token = "EOF"
            else:
                token = regex.strip().upper()
        else:
            token = re.sub(r'\W+', '', action.split()[-1])
        
        parts.append(f"({regex_clean})#{token}")
    
    super_regex = "|".join(parts)
    print(f"Super-regex construido: {super_regex}")
    return super_regex
