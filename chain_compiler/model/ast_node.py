class ASTNode:
    def __init__(self, node_type, value, children=None):
        self.type = node_type
        self.value = value
        self.children = children if children is not None else []
    
    def __repr__(self):
        if self.children:
            return f"{self.value}({', '.join(repr(child) for child in self.children)})"
        else:
            return f"{self.value}"
    
    def pretty_print(self, level=0):
        indent = '  ' * level
        result = f"{indent}{self.type}: {self.value}\n"
        for child in self.children:
            result += child.pretty_print(level + 1)
        return result