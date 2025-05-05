class Operator:
    def __init__(self, symbol, precedence, associativity, arity):
        self.symbol = symbol
        self.precedence = precedence
        self.associativity = associativity
        self.arity = arity
    
    def __repr__(self):
        return f"Operator({self.symbol}, prec={self.precedence}, assoc={self.associativity}, arity={self.arity})"

OPERATORS = {
    '|': Operator('|', precedence=1, associativity='left', arity=2),
    '&': Operator('&', precedence=2, associativity='left', arity=2), 
    '*': Operator('*', precedence=3, associativity='right', arity=1),
    '+': Operator('+', precedence=3, associativity='right', arity=1),
    '?': Operator('?', precedence=3, associativity='right', arity=1),
}