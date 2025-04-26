from thelexer import entrypoint

casos = ["123", "+", "if", "foo", "  ", "#comentario\n"]
for s in casos:
    print(f"{s!r} → {entrypoint(s)}")
