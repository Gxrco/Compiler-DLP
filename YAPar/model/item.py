# YAPar/model/item.py

class Item:
    """
    Ítem LR(0) para Closure/Goto:
      lhs:   símbolo del lado izquierdo (string)
      rhs:   lista de símbolos de la producción (List[str])
      dot:   posición del punto en rhs (int)
    """
    def __init__(self, lhs: str, rhs: list[str], dot: int):
        self.lhs = lhs
        self.rhs = rhs
        self.dot = dot

    def __eq__(self, other):
        return (
            isinstance(other, Item)
            and self.lhs == other.lhs
            and self.rhs == other.rhs
            and self.dot == other.dot
        )

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot))

    def __repr__(self):
        before = " ".join(self.rhs[:self.dot])
        after  = " ".join(self.rhs[self.dot:])
        return f"{self.lhs} → {before} • {after}"
