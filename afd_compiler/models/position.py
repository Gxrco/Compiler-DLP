class Position:
    """Representa una posición en una hoja del árbol sintáctico."""
    _next_id = 1

    def __init__(self, symbol):
        self.id = Position._next_id
        Position._next_id += 1
        self.symbol = symbol

    def __eq__(self, other):
        return isinstance(other, Position) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Pos({self.id}:{self.symbol})"

    @classmethod
    def reset_counter(cls):
        """Reinicia el contador de posiciones"""
        cls._next_id = 1
