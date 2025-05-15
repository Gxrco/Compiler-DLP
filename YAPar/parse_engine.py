# YAPar/parse_engine.py

from typing import List, Tuple, Any
from YAPar.model.item import Item
from YAPar.slr_table_generator import build_slr_parsing_table
from YAPar.grammar_parser import parse_file

class ParseError(Exception):
    """Error en tiempo de parseo (desplazamiento/reducción inválido)."""
    pass

def parse_tokens(
    grammar_path: str,
    tokens: List[str]
) -> List[Tuple[int, str]]:
    """
    Dado un listado de tokens (sus nombres), corre el parser SLR(1)
    y devuelve la secuencia de acciones realizadas:
      [(estado_previo, "shift X"|"reduce A -> α"|"accept"), ...]
    Lanza ParseError si encuentra un token inesperado.
    """
    # 1) Reconstruir gramática y producciones
    grammar = parse_file(grammar_path)
    prods = [(p.lhs, p.rhs) for p in grammar.productions]
    start_prime = grammar.start_symbol + "'"

    # 2) Generar tablas SLR(1)
    states, action_tbl, goto_tbl = build_slr_parsing_table(grammar_path)

    # 3) Preparar pilas y log
    state_stack: List[int] = [0]
    symbol_stack: List[str] = []
    log: List[Tuple[int, str]] = []

    # 4) Procesar cada token + EOF
    input_sequence = tokens + [grammar.eof_token]
    for a in input_sequence:
        while True:
            s = state_stack[-1]
            act = action_tbl.get((s, a))
            if act is None:
                raise ParseError(f"Unexpected token '{a}' in state {s}")
            kind, target = act

            if kind == 'shift':
                # Desplaza: apila símbolo y estado
                log.append((s, f"shift {a}"))
                symbol_stack.append(a)
                state_stack.append(target)
                break  # avance al siguiente token

            elif kind == 'reduce':
                # Reduce: A -> α
                lhs, rhss = prods[target]  # rhss: lista de alternativas
                # Encontrar la alternativa que corresponde al tope de la pila
                chosen_rhs = None
                for alt in rhss:
                    l = len(alt)
                    # Comparamos sufijo de symbol_stack con alt
                    if l <= len(symbol_stack) and symbol_stack[-l:] == alt:
                        chosen_rhs = alt
                        break
                # Si no se encontró, usamos la única alternativa o la más corta
                if chosen_rhs is None:
                    if len(rhss) == 1:
                        chosen_rhs = rhss[0]
                    else:
                        chosen_rhs = min(rhss, key=len)

                # Desapilar |chosen_rhs| símbolos y estados
                for _ in chosen_rhs:
                    symbol_stack.pop()
                    state_stack.pop()

                log.append((s, f"reduce {lhs} -> {' '.join(chosen_rhs)}"))

                # GOTO tras reducción
                s2 = state_stack[-1]
                j = goto_tbl.get((s2, lhs))
                if j is None:
                    raise ParseError(f"No GOTO for '{lhs}' after reduce in state {s2}")
                symbol_stack.append(lhs)
                state_stack.append(j)
                # Repetimos el mismo token 'a' sin avanzar


            elif kind == 'accept':
                log.append((s, "accept"))
                return log

            else:
                raise ParseError(f"Unknown action kind '{kind}' at state {s}")
    return log
