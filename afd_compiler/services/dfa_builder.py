from chain_compiler.model.ast_node import ASTNode
from ..models.position import Position
from ..models.dfa import DFA
from ..utils.ast_functions import (
    traverse_tree, 
    calculate_node_functions, 
    calculate_followpos, 
    get_alphabet
)

def build_direct_dfa(ast, token_names):
    """
    Construye un DFA a partir del AST de la super-regex con marcadores únicos.
    Args:
        ast (ASTNode): AST que ya incluye, tras cada alternativa, un carácter chr(1),chr(2),…
        token_names (list[str]): nombres de token en el mismo orden de las alternativas
    Returns:
        DFA: autómata con state_tokens bien mapeado
    """
    # 1) Reiniciar contador de posiciones
    Position.reset_counter()

    # 2) Inicializar nullable, firstpos y lastpos
    for node in traverse_tree(ast):
        node.nullable = False
        node.firstpos = set()
        node.lastpos = set()

    # 3) Calcular funciones de nodo y followpos
    calculate_node_functions(ast)
    followpos = calculate_followpos(ast)

    # 4) Construir alfabeto real (excluyendo códigos de control < chr(32))
    alphabet = {c for c in get_alphabet(ast) if ord(c) >= 32}

    # 5) Estado inicial
    initial_state = frozenset(ast.firstpos)
    states = {initial_state}
    unmarked = [initial_state]
    transitions = {}
    accepting_states = set()
    state_tokens = {}

    # 6) Preparar mapa de “marcador → índice de token”
    marker_chars = [chr(i+1) for i in range(len(token_names))]
    marker_positions = {pos for pos in ast.lastpos if pos.symbol in marker_chars}
    marker_map = {pos: marker_chars.index(pos.symbol) for pos in marker_positions}

    # 7) Construcción del DFA (algoritmo de estado-estado)
    while unmarked:
        T = unmarked.pop()
        # ¿es estado de aceptación?
        inter = marker_positions & set(T)
        if inter:
            accepting_states.add(T)
            # elegimos el token de menor índice (prioridad de reglas)
            idx = min(marker_map[p] for p in inter)
            state_tokens[T] = token_names[idx]

        # transiciones para cada símbolo real
        for a in alphabet:
            U = set()
            for p in T:
                if p.symbol == a:
                    U.update(followpos.get(p, set()))
            if U:
                U_frozen = frozenset(U)
                transitions[(T, a)] = U_frozen
                if U_frozen not in states:
                    states.add(U_frozen)
                    unmarked.append(U_frozen)

    # 8) Devolver DFA con su mapeo de estados aceptantes a tokens
    dfa = DFA(states, alphabet, transitions, initial_state, accepting_states, state_tokens)
    return dfa
    """
    Construye un AFD a partir del AST de la super-regex,
    usando los marcadores (chr(1),chr(2),…) para asignar tokens.
    
    Args:
        ast (ASTNode): raíz del AST de la super-regex.
        token_names (list[str]): lista de nombres de token, donde
            token_names[i] corresponde al marcador chr(i+1).
    """
    Position.reset_counter()
    
    # Inicializar funciones de nodos
    for node in traverse_tree(ast):
        node.nullable  = False
        node.firstpos = set()
        node.lastpos  = set()
    
    # Calcular nullable, firstpos, lastpos
    calculate_node_functions(ast)
    followpos = calculate_followpos(ast)
    
    # El alfabeto SÍ incluye los marcadores (chr(1)...chr(n))
    alphabet = get_alphabet(ast)
    
    # Estado inicial: conjunto firstpos del root
    initial = frozenset(ast.firstpos)
    states = {initial}
    unmarked = [initial]
    transitions = {}
    accepting = set()
    state_tokens = {}
    
    # Marcadores efectivos: chr(1), chr(2), ..., chr(len(token_names))
    markers = [chr(i+1) for i in range(len(token_names))]
    
    # Construcción clásica
    while unmarked:
        S = unmarked.pop()
        
        # Si S contiene alguna posición cuyo symbol es marcador:
        # determinamos cuál y asignamos token
        markers_in_S = [pos.symbol for pos in S if pos.symbol in markers]
        if markers_in_S:
            # Si hay varios, Lex prioriza el orden de definición (primero en token_names)
            # así que tomamos el de menor índice:
            idx = min(markers.index(m) for m in markers_in_S)
            accepting.add(S)
            state_tokens[S] = token_names[idx]
        
        # Transiciones
        for a in alphabet:
            # nextpos(S,a)
            U = set()
            for pos in S:
                if pos.symbol == a:
                    U.update(followpos.get(pos, ()))
            if U:
                U = frozenset(U)
                transitions[(S,a)] = U
                if U not in states:
                    states.add(U)
                    unmarked.append(U)
    
    return DFA(
        states,
        alphabet,
        transitions,
        initial,
        accepting,
        state_tokens
    )