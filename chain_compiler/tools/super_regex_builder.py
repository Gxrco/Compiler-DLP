import re

def clean_regex_part(regex):
    """
    Limpia la parte de la expresión regular removiendo comillas innecesarias
    en clases de caracteres y literales.
    """
    regex = regex.strip()
    # Si es una clase de caracteres, remueve comillas internas (por ejemplo, de "['0'-'9']" a "[0-9]")
    if regex.startswith('[') and regex.endswith(']'):
        return regex.replace("'", "")
    # Si está entre comillas, remueve las comillas
    if regex.startswith("'") and regex.endswith("'"):
        return regex[1:-1]
    return regex

def build_super_regex(rules):
    """
    Construye una super expresión regular a partir de una lista de reglas.
    
    Cada regla es una tupla (regex, action) donde action contiene la acción asociada.
    Para cada alternativa se genera la expresión:
       ((<pattern>)&(<token_literal>))
    donde:
      - <pattern> es la parte de la expresión regular (limpia de comillas innecesarias)
      - <token_literal> es el literal que identifica el token (extraído de la acción) y se encierra en comillas simples.
    
    Luego se unen todas las alternativas con el operador OR ('|').
    """
    parts = []
    for regex, action in rules:
        regex = regex.strip()
        regex_clean = clean_regex_part(regex)
        token = "UNKNOWN"
        action = action.strip()
        # Extraer el token de la acción, buscando return con comillas
        m = re.search(r'return\s+[\'"]([^\'"]+)[\'"]', action)
        if m:
            token = m.group(1)
        elif "raise" in action:
            if regex.strip() == "eof":
                token = "EOF"
            else:
                token = regex.strip().upper()
        else:
            token = re.sub(r'\W+', '', action.split()[-1])
        token_literal = "'" + token + "'"
        part = f"(({regex_clean})&({token_literal}))"
        parts.append(part)
    # Une todas las alternativas con el operador OR
    super_regex = "|".join(parts)
    print(f"Super-regex construido: {super_regex}")
    return super_regex
