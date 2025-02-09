"""
Clase para representar nodos del árbol sintáctico.
Cada nodo puede ser un literal o un operador ('|', '.', '*').

Clase hecha en base a la clase Node del proyecto 1 de la materia de Teoría de la Computación.
https://github.com/XavierLopez25/Proyecto1-TC/blob/main/src/Model/node.py
"""
class Node:
    def __init__(self, kind, symbol=None):
        """
        kind: 'leaf', 'concat', 'union' o 'star'
        symbol: para nodos hoja, el símbolo (por ejemplo, 'a', 'b' o '#' para el marcador de fin)
        """
        self.kind = kind
        self.symbol = symbol      
        self.left = None          
        self.right = None         
        self.child = None         
        
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()
        
        self.position = None