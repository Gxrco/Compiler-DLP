# YAPar/utils/visualize_lr0.py

from graphviz import Digraph
from YAPar.lr0_builder import build_lr0_states
from YAPar.utils.closure_goto import closure, goto

def lr0_to_dot(grammar_path: str, output_dot: str = "lr0_states.dot"):
    """
    Genera un archivo DOT que grafica la colección canónica de estados LR(0),
    y lo renderiza a PDF (output_dot.pdf).
    - grammar_path: ruta al archivo .yalp
    - output_dot: nombre base del archivo .dot (sin extensión .pdf)
    """
    from YAPar.grammar_parser import parse_file

    # Reconstruir gramática aumentada
    grammar = parse_file(grammar_path)
    productions = [(p.lhs, p.rhs) for p in grammar.productions]
    start_prime = grammar.start_symbol + "'"
    aug_prods = [(start_prime, [[grammar.start_symbol]])] + productions

    # Construir estados LR(0)
    estados = build_lr0_states(aug_prods, start_prime)

    # Crear grafo de Graphviz
    dot = Digraph(comment="Autómata LR(0)")
    dot.attr(rankdir="LR")

    # Mapear cada estado (set de items) a un nombre I0, I1, …
    estado_nombres = {}
    for i, I in enumerate(estados):
        nombre = f"I{i}"
        estado_nombres[frozenset(I)] = nombre

        # Etiqueta: lista de ítems
        label_lines = []
        for item in sorted(I, key=lambda it: (it.lhs, tuple(it.rhs), it.dot)):
            # Construir representación: "A → α · β"
            before_dot = " ".join(item.rhs[:item.dot])
            after_dot = " ".join(item.rhs[item.dot:])
            if after_dot:
                repr_item = f"{item.lhs} → {before_dot} · {after_dot}"
            else:
                repr_item = f"{item.lhs} → {before_dot} ·"
            label_lines.append(repr_item)

        dot.node(nombre, "\n".join(label_lines), shape="box")

    # Recolectar todos los símbolos (terminales y no terminales)
    all_symbols = set()
    for (_, rhss) in aug_prods:
        for rhs in rhss:
            for sym in rhs:
                all_symbols.add(sym)

    # Agregar transiciones: para cada estado I y símbolo X, si goto(I,X)=J, dibujar arco
    for i, I in enumerate(estados):
        nombre_I = estado_nombres[frozenset(I)]
        for X in all_symbols:
            J = goto(I, X, aug_prods)
            if J:
                nombre_J = estado_nombres.get(frozenset(J))
                if nombre_J:
                    dot.edge(nombre_I, nombre_J, label=X)

    # Guardar y renderizar a PDF
    safe_name = output_dot
    dot.render(filename=safe_name, format="pdf", cleanup=True)
    print(f"Generado: {safe_name}.pdf (Autómata LR(0))")
