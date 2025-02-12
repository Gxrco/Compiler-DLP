from chain_compiler.tools.ast_builder import build_ast
from graphviz import Digraph

def generate_ast(postfix_tokens):
    """
    Genera el Árbol de Sintaxis Abstracta (AST) a partir de la notación postfix.

    Args:
        postfix_tokens (list): Lista de tokens en notación postfix.

    Returns:
        ASTNode: Nodo raíz del AST.
    """
    ast = build_ast(postfix_tokens)
    return ast
  

def build_ast_graph(ast, graph=None, parent=None):
    """
    Función recursiva que agrega nodos y aristas a un objeto Graphviz Digraph
    a partir de un AST.
    
    Args:
        ast: Nodo del AST (se asume que tiene atributos 'value', 'type' y 'children').
        graph: Objeto Digraph de Graphviz.
        parent: Nodo padre (opcional).
    
    Returns:
        graph: Objeto Digraph con el AST representado.
    """
    if graph is None:
        graph = Digraph()
    
    node_id = str(id(ast))
    label = f"{ast.value}\n({ast.type})"
    graph.node(node_id, label)
    
    if parent:
        graph.edge(str(id(parent)), node_id)
    
    for child in ast.children:
        build_ast_graph(child, graph, ast)
    
    return graph