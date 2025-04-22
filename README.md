# Generador de Analizador Léxico - CC3071 

Este proyecto es un generador automatizado de analizadores léxicos que utiliza definiciones escritas en archivos YAL (Yet Another Lexer) para construir expresiones regulares, convertirlas en Autómatas Finitos Deterministas (AFD), optimizarlos, y finalmente utilizarlos para escanear y tokenizar archivos de entrada.

## Estructura General del Proyecto

El proyecto está organizado en los siguientes componentes principales:

- **afd_compiler**: Encargado de construir y optimizar el AFD.
- **chain_compiler**: Encargado de procesar expresiones regulares, generar AST (Abstract Syntax Tree) y manejar su conversión.
- **lex_compiler**: Contiene servicios relacionados con la compilación léxica.
- **file_processor.py**: Gestiona la lectura de archivos con definiciones de expresiones regulares.

## Proceso de Compilación Léxica

### 1. Definición en archivos YAL

Los analizadores léxicos se definen en archivos `.yal` donde se especifican las reglas y tokens con su respectiva acción asociada, por ejemplo:

```yal
rule tokens =
  "if" { return IF }
| [a-zA-Z][a-zA-Z0-9]* { return ID }
| [0-9]+ { return NUMBER }
| "+" { return PLUS }
| [ \t\n\r] { return WHITESPACE }
```

### 2. Procesamiento del archivo YAL

El archivo YAL es procesado para extraer reglas que posteriormente son convertidas en una super-expresión regular. Esta super-expresión agrupa todas las reglas, permitiendo que se genere un único AFD capaz de reconocer todos los patrones simultáneamente.

### 3. Construcción del AST

La super-expresión regular es transformada en un Árbol Sintáctico Abstracto (AST) utilizando algoritmos de conversión de expresiones regulares a notación postfix, seguido de la construcción del AST a través del método del algoritmo Shunting Yard.

### 4. Generación del AFD

El AST generado es utilizado para construir un Autómata Finito Determinista (AFD) mediante el método directo, en el que cada estado del autómata representa un conjunto de posiciones del AST.

### 5. Optimización del AFD

Una vez construido, el AFD es optimizado utilizando el algoritmo de Hopcroft para reducir el número de estados y transiciones, obteniendo así un analizador léxico más eficiente.

### 6. Tokenización del archivo de entrada

Finalmente, el AFD optimizado se utiliza para escanear un archivo de entrada línea por línea. El escáner identifica tokens basándose en las definiciones originales del archivo YAL, generando una tabla de símbolos que contiene el tipo de token, el lexema correspondiente y la ubicación en el archivo fuente.

## Ejecución del Proyecto

Para ejecutar el generador de analizadores léxicos, utiliza:

```shell
python app.py --yal ejemplo3.yal --scan_file input.txt
```

Esto generará y visualizará el AFD correspondiente y realizará el escaneo del archivo proporcionado, mostrando la tabla de símbolos resultante en consola.

## Visualización de Resultados

El proyecto genera archivos visuales utilizando Graphviz que ilustran claramente:

- El AST generado a partir de la expresión regular.
- El AFD inicial construido.
- El AFD minimizado final.

Estos gráficos facilitan la comprensión y depuración del proceso de generación del analizador léxico.

## Conclusión

Este proyecto permite generar analizadores léxicos robustos y optimizados automáticamente a partir de definiciones simples en archivos YAL, simplificando enormemente la tarea de implementación de analizadores léxicos para lenguajes de programación u otros sistemas de análisis de texto.

