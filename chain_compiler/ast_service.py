from chain_compiler.tools.ast_builder import build_ast
from graphviz import Digraph

def generate_ast(postfix_tokens):
    ast = build_ast(postfix_tokens)
    return ast
  

def build_ast_graph(ast, graph=None, parent=None):
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