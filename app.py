import argparse
import re
from chain_compiler.normalizer import normalize_regex
from chain_compiler.parser import parse_tokens
from chain_compiler.ast_service import generate_ast, build_ast_graph
from afd_compiler.service import AFDService
from file_processor import read_regex_from_file
from chain_compiler.tools.yal_parser import parse_yal_file
from chain_compiler.tools.super_regex_builder import build_super_regex
from lex_compiler.service import generate_lexer_py
import sys



import re

def scan_input_file(filepath, yal_rules):
    """
    Escanea un archivo de entrada y genera una tabla de símbolos.
    Implementación robusta y genérica que maneja cualquier archivo .yal.
    
    Args:
        filepath (str): Ruta al archivo de entrada a analizar
        yal_rules (list): Reglas extraídas del archivo .yal (tuplas de regex, token, función)
        
    Returns:
        list: Tabla de símbolos con los tokens reconocidos
    """
    print(f"Iniciando escaneo del archivo: {filepath}")
    
    # Compilar patrones
    patterns = []
    
    # Diccionario de caracteres especiales y sus tokens correspondientes
    special_chars = {
        '{': 'LBRACE',
        '}': 'RBRACE',
        '[': 'LBRACKET',
        ']': 'RBRACKET',
        '(': 'LPAREN',
        ')': 'RPAREN',
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'TIMES',
        '/': 'DIVIDE',
        '=': 'ASSIGN',
        '<': 'LESS',
        '>': 'GREATER',
        '!': 'EXCLAMATION',
        ':': 'COLON',
        ';': 'SEMICOLON',
        ',': 'COMMA',
        '.': 'DOT',
        '&': 'AMPERSAND',
        '|': 'PIPE',
        '^': 'CARET',
        '%': 'PERCENT',
        '~': 'TILDE',
        '@': 'AT',
        '#': 'HASH'
    }
    
    # Operadores compuestos y sus tokens
    compound_operators = {
        '==': 'EQUALS',
        '!=': 'NOTEQUAL',
        '<=': 'LESSEQ',
        '>=': 'GREATEREQ',
        '&&': 'LOGICAL_AND',
        '||': 'LOGICAL_OR',
        '++': 'INCREMENT',
        '--': 'DECREMENT',
        '+=': 'PLUS_ASSIGN',
        '-=': 'MINUS_ASSIGN',
        '*=': 'TIMES_ASSIGN',
        '/=': 'DIVIDE_ASSIGN'
    }
    
    # Palabras clave comunes y sus tokens
    keywords = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'return': 'RETURN',
        'break': 'BREAK',
        'continue': 'CONTINUE',
        'switch': 'SWITCH',
        'case': 'CASE',
        'default': 'DEFAULT',
        'true': 'TRUE',
        'false': 'FALSE',
        'null': 'NULL',
        'void': 'VOID',
        'int': 'INT',
        'float': 'FLOAT',
        'double': 'DOUBLE',
        'char': 'CHAR',
        'string': 'STRING',
        'bool': 'BOOL',
        'class': 'CLASS',
        'struct': 'STRUCT',
        'function': 'FUNCTION',
        'var': 'VAR',
        'let': 'LET',
        'const': 'CONST'
    }
    
    # Verificar qué tokens están definidos en las reglas
    defined_tokens = {}
    for regex, token, func in yal_rules:
        defined_tokens[token] = True
        
        # Compilar patrón
        pat_text = regex.strip()
        
        # Escapar correctamente los caracteres especiales en expresiones regulares
        if pat_text in special_chars or pat_text in '[]{}().*+?^$\\':
            # Asegurar que estén correctamente escapados para regex
            if pat_text in '[]{}().*+?^$\\':
                pat_text = '\\' + pat_text
        
        try:
            print(f"Compilando patrón: '{pat_text}' -> {token}")
            patterns.append((re.compile(rf'^{pat_text}'), token, func))
        except re.error as e:
            print(f"Error compilando '{pat_text}': {e}")
            try:
                escaped_pat = re.escape(pat_text)
                print(f"  Usando versión escapada: '{escaped_pat}'")
                patterns.append((re.compile(rf'^{escaped_pat}'), token, func))
            except re.error as e2:
                print(f"  Error en fallback: {e2}")
    
    # Tokens importantes que deben definirse
    required_tokens = {
        'LBRACE': ('\\{', lambda x: 'LBRACE'),
        'RBRACE': ('\\}', lambda x: 'RBRACE'),
        'LBRACKET': ('\\[', lambda x: 'LBRACKET'),
        'RBRACKET': ('\\]', lambda x: 'RBRACKET'),
        'LPAREN': ('\\(', lambda x: 'LPAREN'),
        'RPAREN': ('\\)', lambda x: 'RPAREN'),
        'PLUS': ('\\+', lambda x: 'PLUS'),
        'MINUS': ('\\-', lambda x: 'MINUS'),
        'TIMES': ('\\*', lambda x: 'TIMES'),
        'DIVIDE': ('/', lambda x: 'DIVIDE'),
        'ASSIGN': ('=', lambda x: 'ASSIGN'),
        'SEMICOLON': (';', lambda x: 'SEMICOLON'),
        'COLON': (':', lambda x: 'COLON'),
        'COMMA': (',', lambda x: 'COMMA')
    }
    
    # Añadir tokens requeridos si no están definidos
    for token, (pattern, func) in required_tokens.items():
        if token not in defined_tokens:
            try:
                patterns.append((re.compile(f'^{pattern}'), token, func))
                print(f"Añadido patrón especial para {token}: '{pattern}'")
            except re.error as e:
                print(f"Error al añadir patrón para {token}: {e}")
    
    # Añadir patrones para comentarios si no están definidos
    if 'COMMENT' not in defined_tokens:
        try:
            patterns.append((re.compile(r'^#[^\n]*'), 'COMMENT', lambda x: 'COMMENT'))
            print("Añadido patrón para comentarios: '#[^\\n]*'")
        except re.error as e:
            print(f"Error al añadir patrón para comentarios: {e}")
    
    # Añadir patrones para identificadores si no están definidos
    if 'ID' not in defined_tokens:
        try:
            patterns.append((re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*'), 'ID', lambda x: 'ID'))
            print("Añadido patrón para identificadores: '[a-zA-Z][a-zA-Z0-9_]*'")
        except re.error as e:
            print(f"Error al añadir patrón para identificadores: {e}")
    
    # Añadir patrones para números si no están definidos
    if 'NUMBER' not in defined_tokens:
        try:
            patterns.append((re.compile(r'^[0-9]+(\.[0-9]+)?'), 'NUMBER', lambda x: 'NUMBER'))
            print("Añadido patrón para números: '[0-9]+(\\.[0-9]+)?'")
        except re.error as e:
            print(f"Error al añadir patrón para números: {e}")
    
    # Añadir patrones para espacios en blanco si no están definidos
    if 'WHITESPACE' not in defined_tokens:
        try:
            patterns.append((re.compile(r'^[ \t\n\r]+'), 'WHITESPACE', lambda x: 'WHITESPACE'))
            print("Añadido patrón para espacios en blanco: '[ \\t\\n\\r]+'")
        except re.error as e:
            print(f"Error al añadir patrón para espacios en blanco: {e}")
    
    # Escanear archivo
    table = []
    try:
        with open(filepath, encoding='utf-8') as f:
            for lineno, line in enumerate(f, 1):
                truncated = line[:30] + "..." if len(line) > 30 else line
                print(f"Procesando línea {lineno}: {truncated}")
                pos = 0
                while pos < len(line):
                    # Intentar coincidencia con todos los patrones
                    best = None
                    for pat, tok, func in patterns:
                        try:
                            m = pat.match(line[pos:])
                            if m and (not best or len(m.group(0)) > len(best[0])):
                                best = (m.group(0), tok, func)
                        except Exception as e:
                            print(f"Error al intentar coincidencia con patrón {pat.pattern}: {e}")
                    
                    # Si no se encontró coincidencia, manejar caracteres especiales directamente
                    if not best:
                        char = line[pos]
                        
                        # Verificar si es un operador compuesto
                        compound = False
                        if pos + 1 < len(line):
                            two_chars = line[pos:pos+2]
                            if two_chars in compound_operators:
                                token = compound_operators[two_chars]
                                table.append({"line": lineno, "token": token, "lexeme": two_chars, "value": token})
                                pos += 2
                                compound = True
                        
                        # Si no es compuesto, verificar caracteres individuales
                        if not compound:
                            if char in special_chars:
                                token = special_chars[char]
                                table.append({"line": lineno, "token": token, "lexeme": char, "value": token})
                            elif char.isalpha():
                                # Extraer identificador completo
                                j = pos + 1
                                while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                                    j += 1
                                id_str = line[pos:j]
                                
                                # Verificar si es una palabra clave
                                if id_str.lower() in keywords:
                                    token = keywords[id_str.lower()]
                                else:
                                    token = "ID"
                                    
                                table.append({"line": lineno, "token": token, "lexeme": id_str, "value": token})
                                pos += len(id_str)
                                continue
                            elif char.isdigit():
                                # Extraer número completo
                                j = pos + 1
                                while j < len(line) and (line[j].isdigit() or line[j] == '.'):
                                    j += 1
                                num_str = line[pos:j]
                                table.append({"line": lineno, "token": "NUMBER", "lexeme": num_str, "value": "NUMBER"})
                                pos += len(num_str)
                                continue
                            elif char in ' \t\n\r':
                                # Extraer espacio en blanco completo
                                j = pos + 1
                                while j < len(line) and line[j] in ' \t\n\r':
                                    j += 1
                                ws_str = line[pos:j]
                                table.append({"line": lineno, "token": "WHITESPACE", "lexeme": ws_str, "value": "WHITESPACE"})
                                pos += len(ws_str)
                                continue
                            else:
                                table.append({"line": lineno, "token": "ERROR", "lexeme": char, "value": "ERROR"})
                            pos += 1
                    else:
                        # Procesar la coincidencia encontrada
                        lexeme, token, func = best
                        try:
                            value = func(lexeme)
                            table.append({"line": lineno, "token": token, "lexeme": lexeme, "value": value})
                            pos += len(lexeme)
                        except Exception as e:
                            print(f"Error procesando lexema '{lexeme}' con función {func}: {e}")
                            pos += 1
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
    
    # Imprimir tabla
    print("\nTabla de símbolos:")
    for entry in table:
        print(entry)
    
    return table

def process_regex(super_regex, test_strings=None):
    """
    Procesa una expresión regular, construye el AST, el DFA normal y minimizado.
    Versión mejorada para manejar errores y límites en los nombres de archivos.
    
    Args:
        super_regex (str): La expresión regular a procesar
        test_strings (list): Lista opcional de cadenas para probar
    
    Returns:
        AFDService: La instancia del servicio AFD con el DFA construido
    """
    print("Expresión regular:", super_regex)
    
    try:
        # Tokenizar la regex
        tokens = normalize_regex(super_regex)
        print("Tokens normalizados:", tokens)
        
        # Convertir a notación postfix
        postfix = parse_tokens(tokens)
        print("Notación postfix:", postfix)
        
        # Generar el AST
        ast = generate_ast(postfix)
        print("AST:")
        print(ast.pretty_print())
        
        # Construir y visualizar el AST - Con manejo de errores
        try:
            ast_graph = build_ast_graph(ast)
            ast_graph.render('ast_graph', view=False)
        except Exception as e:
            print(f"Error al generar el gráfico del AST: {e}")
        
        # Construir el DFA a partir del AST
        afd_service = AFDService()
        dfa = afd_service.build_dfa_from_ast(ast)
        
        # Usar nombres de archivo más seguros
        try:
            # Generar un nombre de archivo seguro para el DFA normal
            normal_filename = 'dfa_normal'
            dfa.visualize(normal_filename)
        except Exception as e:
            print(f"Error al visualizar el DFA normal: {e}")
        
        # Minimizar el DFA con manejo de errores
        try:
            minimized_dfa = afd_service.minimize_dfa()
            
            # Generar un nombre de archivo seguro para el DFA minimizado
            minimized_filename = 'dfa_minimized'
            minimized_dfa.visualize(minimized_filename)
        except Exception as e:
            print(f"Error al minimizar o visualizar el DFA: {e}")
            minimized_dfa = dfa  # Usar el DFA original si falla la minimización
        
        # Probar cadenas si se proporcionan
        if test_strings:
            print("\nProbando cadenas con el AFD minimizado:")
            for s in test_strings:
                result = afd_service.match(s)
                status = 'Aceptada' if result else 'Rechazada'
                token = f" (Token: {result})" if result else ""
                print(f"'{s}': {status}{token}")
        
        return afd_service
        
    except Exception as e:
        print(f"Error en el procesamiento de la regex: {e}")
        raise  # Re-lanzar la excepción para depuración

def make_action(action):
    action = action.strip()

    # Caso especial: devolver el propio lexema
    if re.match(r'return\s+lexbuf', action):
        return lambda lxm: lxm

    # Extraer lo que sigue a return
    m = re.search(r'return\s+(.+?);?$', action)
    if m:
        expr = m.group(1).strip()

        # Si es un identificador simple (token name), devuélvelo como string
        if re.fullmatch(r'[A-Za-z_]\w*', expr):
            return lambda lxm, t=expr: t

        # De lo contrario, compile como expresión Python (e.g. int(lxm))
        code = compile(f"lambda lxm: {expr}", "<action>", "eval")
        return eval(code)

    # Raise EOF
    if "raise" in action:
        return lambda lxm: (_ for _ in ()).throw(Exception("EOF"))

    return lambda lxm: None



def process_yal_file(path, scan_file=None, test_strings=None):
    info = parse_yal_file(path)
    yal_rules = []
    for regex, action in info["alternatives"]:
        # Primero busca return "TOKEN" o return 'TOKEN'
        m = re.search(r'return\s+[\'"]([^\'"]+)[\'"]', action)
        if m:
            token = m.group(1)
        else:
            # Si no hay comillas, capturar palabra tras return
            m2 = re.search(r'return\s+([A-Za-z_]\w*)', action)
            if m2:
                token = m2.group(1)
            elif "raise" in action:
                token = "EOF"
            else:
                token = "UNKNOWN"

        func = make_action(action)
        clean = regex.strip().replace("'", "").replace('"', "")
        yal_rules.append((clean, token, func))
        
    super_regex = build_super_regex(info["alternatives"])
    afd = process_regex(super_regex)
    if scan_file:
        scan_input_file(scan_file, yal_rules)
    return afd


if __name__ == '__main__':
    import argparse
    import sys
    import os
    import importlib.util

    parser = argparse.ArgumentParser(
        description='Generador de lexer a partir de .yal y escáner opcional')
    parser.add_argument(
        '--yal',
        required=True,
        help='Ruta a un archivo .yal')
    parser.add_argument(
        '--scan_file',
        help='(Opcional) Ruta a un archivo para escaneo con el lexer generado')
    parser.add_argument(
        '--out', '-o',
        default='thelexer.py',
        help='Ruta de salida para el lexer generado (p.ej. thelexer.py)')
    args = parser.parse_args()

    # 1) Parsear .yal
    yal_info = parse_yal_file(args.yal)
    if yal_info is None:
        sys.exit(1)

    # 2) Generar el lexer Python
    generate_lexer_py(yal_info, args.out)
    print(f"✅ Lexer generado en {args.out}")

    # 3) Si se pidió escaneo, cargar y ejecutar entrypoint del lexer
    if args.scan_file:
        spec = importlib.util.spec_from_file_location(
            "thelexer", os.path.abspath(args.out))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        data = open(args.scan_file, encoding='utf-8').read()
        for tok, lex in mod.entrypoint(data):
            print(tok, lex)
