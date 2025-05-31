#!/usr/bin/env python3
# Parser generado por YAPar CLI

PRODUCTIONS = [('program', [['stmt_list']]), ('stmt_list', [['stmt_list', 'stmt'], ['stmt']]), ('stmt', [['ID', 'ASSIGN', 'expr', 'SEMICOLON'], ['LBRACE', 'stmt_list', 'RBRACE'], ['IF', 'LPAREN', 'expr', 'RPAREN', 'stmt'], ['IF', 'LPAREN', 'expr', 'RPAREN', 'stmt', 'ELSE', 'stmt'], ['WHILE', 'LPAREN', 'expr', 'RPAREN', 'stmt']]), ('expr', [['expr', 'PLUS', 'term'], ['expr', 'MINUS', 'term'], ['term']]), ('term', [['term', 'TIMES', 'factor'], ['term', 'DIVIDE', 'factor'], ['factor']]), ('factor', [['LPAREN', 'expr', 'RPAREN'], ['ID'], ['NUMBER'], ['ID', 'LBRACKET', 'expr', 'RBRACKET']])]

ACTION = {(0, 'IF'): ('shift', 6), (0, 'ID'): ('shift', 4), (0, 'LBRACE'): ('shift', 5), (0, 'WHILE'): ('shift', 7), (1, '$'): ('accept', None), (2, 'IF'): ('shift', 6), (2, 'ID'): ('shift', 4), (2, 'LBRACE'): ('shift', 5), (2, 'WHILE'): ('shift', 7), (2, '$'): ('reduce', 0), (3, 'IF'): ('reduce', 1), (3, '$'): ('reduce', 1), (3, 'RBRACE'): ('reduce', 1), (3, 'WHILE'): ('reduce', 1), (4, 'ASSIGN'): ('shift', 9), (5, 'IF'): ('shift', 6), (5, 'ID'): ('shift', 4), (5, 'LBRACE'): ('shift', 5), (5, 'WHILE'): ('shift', 7), (6, 'LPAREN'): ('shift', 11), (7, 'LPAREN'): ('shift', 12), (8, 'IF'): ('reduce', 1), (8, '$'): ('reduce', 1), (8, 'RBRACE'): ('reduce', 1), (8, 'WHILE'): ('reduce', 1), (9, 'NUMBER'): ('shift', 18), (9, 'ID'): ('shift', 16), (9, 'LPAREN'): ('shift', 17), (10, 'IF'): ('shift', 6), (10, 'ID'): ('shift', 4), (10, 'LBRACE'): ('shift', 5), (10, 'WHILE'): ('shift', 7), (10, 'RBRACE'): ('shift', 19), (11, 'NUMBER'): ('shift', 18), (11, 'ID'): ('shift', 16), (11, 'LPAREN'): ('shift', 17), (12, 'NUMBER'): ('shift', 18), (12, 'ID'): ('shift', 16), (12, 'LPAREN'): ('shift', 17), (13, 'MINUS'): ('shift', 24), (13, 'SEMICOLON'): ('shift', 22), (13, 'PLUS'): ('shift', 23), (14, 'TIMES'): ('shift', 25), (14, 'PLUS'): ('reduce', 3), (14, 'RPAREN'): ('reduce', 3), (14, 'RBRACKET'): ('reduce', 3), (14, 'SEMICOLON'): ('reduce', 3), (14, 'MINUS'): ('reduce', 3), (14, 'DIVIDE'): ('shift', 26), (15, 'RPAREN'): ('reduce', 4), (15, 'RBRACKET'): ('reduce', 4), (15, 'DIVIDE'): ('reduce', 4), (15, 'SEMICOLON'): ('reduce', 4), (15, 'PLUS'): ('reduce', 4), (15, 'TIMES'): ('reduce', 4), (15, 'MINUS'): ('reduce', 4), (16, 'RPAREN'): ('reduce', 5), (16, 'RBRACKET'): ('reduce', 5), (16, 'DIVIDE'): ('reduce', 5), (16, 'SEMICOLON'): ('reduce', 5), (16, 'PLUS'): ('reduce', 5), (16, 'TIMES'): ('reduce', 5), (16, 'MINUS'): ('reduce', 5), (16, 'LBRACKET'): ('shift', 27), (17, 'NUMBER'): ('shift', 18), (17, 'ID'): ('shift', 16), (17, 'LPAREN'): ('shift', 17), (18, 'RPAREN'): ('reduce', 5), (18, 'RBRACKET'): ('reduce', 5), (18, 'DIVIDE'): ('reduce', 5), (18, 'SEMICOLON'): ('reduce', 5), (18, 'PLUS'): ('reduce', 5), (18, 'TIMES'): ('reduce', 5), (18, 'MINUS'): ('reduce', 5), (19, 'WHILE'): ('reduce', 2), (19, '$'): ('reduce', 2), (19, 'RBRACE'): ('reduce', 2), (19, 'IF'): ('reduce', 2), (19, 'ELSE'): ('reduce', 2), (20, 'RPAREN'): ('shift', 29), (20, 'PLUS'): ('shift', 23), (20, 'MINUS'): ('shift', 24), (21, 'MINUS'): ('shift', 24), (21, 'RPAREN'): ('shift', 30), (21, 'PLUS'): ('shift', 23), (22, 'WHILE'): ('reduce', 2), (22, '$'): ('reduce', 2), (22, 'RBRACE'): ('reduce', 2), (22, 'IF'): ('reduce', 2), (22, 'ELSE'): ('reduce', 2), (23, 'NUMBER'): ('shift', 18), (23, 'ID'): ('shift', 16), (23, 'LPAREN'): ('shift', 17), (24, 'NUMBER'): ('shift', 18), (24, 'ID'): ('shift', 16), (24, 'LPAREN'): ('shift', 17), (25, 'NUMBER'): ('shift', 18), (25, 'ID'): ('shift', 16), (25, 'LPAREN'): ('shift', 17), (26, 'NUMBER'): ('shift', 18), (26, 'ID'): ('shift', 16), (26, 'LPAREN'): ('shift', 17), (27, 'NUMBER'): ('shift', 18), (27, 'ID'): ('shift', 16), (27, 'LPAREN'): ('shift', 17), (28, 'RPAREN'): ('shift', 36), (28, 'MINUS'): ('shift', 24), (28, 'PLUS'): ('shift', 23), (29, 'IF'): ('shift', 6), (29, 'ID'): ('shift', 4), (29, 'LBRACE'): ('shift', 5), (29, 'WHILE'): ('shift', 7), (30, 'IF'): ('shift', 6), (30, 'ID'): ('shift', 4), (30, 'LBRACE'): ('shift', 5), (30, 'WHILE'): ('shift', 7), (31, 'TIMES'): ('shift', 25), (31, 'PLUS'): ('reduce', 3), (31, 'RPAREN'): ('reduce', 3), (31, 'RBRACKET'): ('reduce', 3), (31, 'SEMICOLON'): ('reduce', 3), (31, 'MINUS'): ('reduce', 3), (31, 'DIVIDE'): ('shift', 26), (32, 'PLUS'): ('reduce', 3), (32, 'RPAREN'): ('reduce', 3), (32, 'RBRACKET'): ('reduce', 3), (32, 'SEMICOLON'): ('reduce', 3), (32, 'MINUS'): ('reduce', 3), (32, 'TIMES'): ('shift', 25), (32, 'DIVIDE'): ('shift', 26), (33, 'RPAREN'): ('reduce', 4), (33, 'RBRACKET'): ('reduce', 4), (33, 'DIVIDE'): ('reduce', 4), (33, 'SEMICOLON'): ('reduce', 4), (33, 'PLUS'): ('reduce', 4), (33, 'TIMES'): ('reduce', 4), (33, 'MINUS'): ('reduce', 4), (34, 'RPAREN'): ('reduce', 4), (34, 'RBRACKET'): ('reduce', 4), (34, 'DIVIDE'): ('reduce', 4), (34, 'SEMICOLON'): ('reduce', 4), (34, 'PLUS'): ('reduce', 4), (34, 'TIMES'): ('reduce', 4), (34, 'MINUS'): ('reduce', 4), (35, 'RBRACKET'): ('shift', 39), (35, 'MINUS'): ('shift', 24), (35, 'PLUS'): ('shift', 23), (36, 'RPAREN'): ('reduce', 5), (36, 'RBRACKET'): ('reduce', 5), (36, 'DIVIDE'): ('reduce', 5), (36, 'SEMICOLON'): ('reduce', 5), (36, 'PLUS'): ('reduce', 5), (36, 'TIMES'): ('reduce', 5), (36, 'MINUS'): ('reduce', 5), (37, 'ELSE'): ('reduce', 2), (37, 'WHILE'): ('reduce', 2), (37, '$'): ('reduce', 2), (37, 'RBRACE'): ('reduce', 2), (37, 'IF'): ('reduce', 2), (38, 'WHILE'): ('reduce', 2), (38, '$'): ('reduce', 2), (38, 'RBRACE'): ('reduce', 2), (38, 'IF'): ('reduce', 2), (38, 'ELSE'): ('reduce', 2), (39, 'RPAREN'): ('reduce', 5), (39, 'RBRACKET'): ('reduce', 5), (39, 'DIVIDE'): ('reduce', 5), (39, 'SEMICOLON'): ('reduce', 5), (39, 'PLUS'): ('reduce', 5), (39, 'TIMES'): ('reduce', 5), (39, 'MINUS'): ('reduce', 5), (40, 'IF'): ('shift', 6), (40, 'ID'): ('shift', 4), (40, 'LBRACE'): ('shift', 5), (40, 'WHILE'): ('shift', 7), (41, 'WHILE'): ('reduce', 2), (41, '$'): ('reduce', 2), (41, 'RBRACE'): ('reduce', 2), (41, 'IF'): ('reduce', 2), (41, 'ELSE'): ('reduce', 2)}

GOTO = {(0, 'stmt'): 3, (0, 'program'): 1, (0, 'stmt_list'): 2, (2, 'stmt'): 8, (5, 'stmt'): 3, (5, 'stmt_list'): 10, (9, 'expr'): 13, (9, 'factor'): 15, (9, 'term'): 14, (10, 'stmt'): 8, (11, 'expr'): 20, (11, 'factor'): 15, (11, 'term'): 14, (12, 'expr'): 21, (12, 'factor'): 15, (12, 'term'): 14, (17, 'expr'): 28, (17, 'factor'): 15, (17, 'term'): 14, (23, 'factor'): 15, (23, 'term'): 31, (24, 'factor'): 15, (24, 'term'): 32, (25, 'factor'): 33, (26, 'factor'): 34, (27, 'expr'): 35, (27, 'factor'): 15, (27, 'term'): 14, (29, 'stmt'): 37, (30, 'stmt'): 38, (40, 'stmt'): 41}

def parse(tokens):
    """Parser SLR(1) autónomo: recibe lista de token names y devuelve acciones."""
    state_stack = [0]
    symbol_stack = []
    log = []
    tokens = tokens + ['$']  # agregamos EOF al final
    for a in tokens:
        while True:
            s = state_stack[-1]
            act = ACTION.get((s, a))
            if act is None:
                raise Exception(f"Token inesperado '{a}' en estado {s}")
            kind, target = act
            if kind == 'shift':
                log.append((s, f"shift {a}"))
                symbol_stack.append(a)
                state_stack.append(target)
                break  # avanzamos al siguiente token
            elif kind == 'reduce':
                lhs, rhs_list = PRODUCTIONS[target]
                chosen_rhs = None
                for alt in rhs_list:
                    if len(alt) <= len(symbol_stack) and symbol_stack[-len(alt):] == alt:
                        chosen_rhs = alt
                        break
                if chosen_rhs is None:
                    chosen_rhs = rhs_list[0]
                for _ in chosen_rhs:
                    symbol_stack.pop()
                    state_stack.pop()
                log.append((s, f"reduce {lhs} -> {' '.join(chosen_rhs)}"))
                s2 = state_stack[-1]
                j = GOTO.get((s2, lhs))
                if j is None:
                    raise Exception(f"No hay GOTO para '{lhs}' en estado {s2}")
                symbol_stack.append(lhs)
                state_stack.append(j)
                continue
            elif kind == 'accept':
                log.append((s, 'accept'))
                return log
            else:
                raise Exception(f"Acción desconocida '{kind}' en estado {s}")
    return log

if __name__ == '__main__':
    import sys
    data = sys.stdin.read().split()
    try:
        result = parse(data)
        for state, action in result:
            print(state, action)
    except Exception as e:
        print('Error durante el parseo:', e)
