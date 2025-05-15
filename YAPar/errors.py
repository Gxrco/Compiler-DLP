# YAPar/errors.py

class YAParError(Exception):
    """Error base de YAPar."""
    pass

class GrammarError(YAParError):
    """Se produce cuando falla la carga o el parseo de la gramática."""
    pass

class GenerationError(YAParError):
    """Se produce durante la generación de código o escritura de archivos."""
    pass

class CLIError(YAParError):
    """Se produce al procesar argumentos o durante la ejecución del CLI."""
    pass
