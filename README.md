# Compiler-DLP Project: Generador Completo de Analizadores Léxicos y Sintácticos

**AUTORES:** 
- Gerson Ramírez, 22281
- Diego Valenzuela, 22309

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [YALex: Generador de Analizadores Léxicos](#yalex-generador-de-analizadores-léxicos)
4. [YAPar: Generador de Analizadores Sintácticos](#yapar-generador-de-analizadores-sintácticos)
5. [Pipeline de Orquestación](#pipeline-de-orquestación)
6. [Instalación y Configuración](#instalación-y-configuración)
7. [Uso Completo del Sistema](#uso-completo-del-sistema)
8. [Ejemplos Prácticos](#ejemplos-prácticos)
9. [Detalles Técnicos](#detalles-técnicos)
10. [Testing y Validación](#testing-y-validación)
11. [Visualización de Resultados](#visualización-de-resultados)

## Descripción General

Este proyecto implementa un **sistema completo de generación de compiladores** que consta de dos módulos principales interconectados:

- **YALex**: Generador de analizadores léxicos basado en expresiones regulares
- **YAPar**: Generador de analizadores sintácticos SLR(1) basado en gramáticas libres de contexto

El sistema permite definir la sintaxis de un lenguaje de programación mediante archivos de especificación y generar automáticamente analizadores que pueden procesar código fuente, detectar errores léxicos y sintácticos, y validar la corrección del programa.

### Objetivos Cumplidos

✅ **Implementación de YALex** para producir tokens desde archivos de especificaciones regulares  
✅ **Construcción de Autómatas LR(0)** con cálculo de funciones FIRST, FOLLOW y CLOSURE  
✅ **Generación de tablas SLR(1)** a partir de autómatas LR(0)  
✅ **Evaluación de cadenas de entrada** para determinar corrección sintáctica  
✅ **Detección y reporte de errores** sintácticos y gramaticales durante el parseo  

## Arquitectura del Proyecto

```
Compiler-DLP/
├── YALex/                          # Generador de Analizadores Léxicos
│   ├── chain_compiler/             # Procesamiento de expresiones regulares
│   │   ├── tools/                  # Herramientas de parsing y construcción
│   │   │   ├── yal_parser.py      # Parser de archivos .yal
│   │   │   ├── super_regex_builder.py # Constructor de super-regex
│   │   │   ├── regex_parser.py     # Tokenizador de expresiones regulares
│   │   │   └── ast_builder.py      # Constructor de AST
│   │   ├── model/                  # Modelos de datos
│   │   │   ├── token.py           # Clase Token
│   │   │   ├── ast_node.py        # Nodos del AST
│   │   │   └── operator.py        # Operadores y precedencias
│   │   ├── normalizer.py          # Normalizador de regex
│   │   ├── parser.py              # Conversor a notación postfix
│   │   └── ast_service.py         # Servicios de AST
│   ├── afd_compiler/              # Constructor y optimizador de DFA
│   │   ├── services/
│   │   │   └── dfa_builder.py     # Constructor directo de DFA
│   │   ├── models/
│   │   │   ├── dfa.py             # Clase DFA principal
│   │   │   └── position.py        # Posiciones en hojas del AST
│   │   ├── tools/
│   │   │   └── dfa_optimization.py # Minimización de DFA (Hopcroft)
│   │   ├── utils/
│   │   │   └── ast_functions.py   # Funciones de análisis del AST
│   │   └── service.py             # Servicio principal de AFD
│   ├── lex_compiler/
│   │   └── service.py             # Generador de código del lexer
│   └── app.py                     # CLI principal de YALex
├── YAPar/                         # Generador de Analizadores Sintácticos
│   ├── model/
│   │   ├── item.py                # Ítems LR(0)
│   │   ├── automaton.py           # Modelo de autómata
│   │   └── state.py               # Estados del autómata
│   ├── utils/
│   │   ├── first_follow.py        # Cálculo de conjuntos FIRST y FOLLOW
│   │   ├── closure_goto.py        # Operaciones CLOSURE y GOTO
│   │   └── visualize_lr0.py       # Visualización de autómatas LR(0)
│   ├── lr0_builder.py             # Constructor de colección canónica LR(0)
│   ├── slr_table_generator.py     # Generador de tablas SLR(1)
│   ├── parse_engine.py            # Motor de parseo
│   ├── grammar_parser.py          # Parser de gramáticas .yalp
│   ├── grammar_ast.py             # AST de gramáticas
│   ├── codegen/
│   │   └── generator.py           # Generador de código del parser
│   └── cli.py                     # CLI principal de YAPar
├── pipeline_yalex_yapar.py        # Orquestador principal del sistema
├── script.py                      # Script de demostración y testing
└── test_lexer_parser.py          # Tests de integración
```

## YALex: Generador de Analizadores Léxicos

### Características Principales

YALex genera analizadores léxicos eficientes a partir de especificaciones en archivos `.yal`. El proceso incluye:

#### 1. **Procesamiento de Especificaciones YAL**
- **Parser de archivos .yal**: Extrae reglas léxicas, headers y trailers
- **Soporte para comentarios**: Maneja comentarios estilo `(* ... *)`
- **Gestión de acciones**: Procesa código a ejecutar cuando se reconoce un patrón

#### 2. **Construcción de Super-Regex**
```python
# Ejemplo de construcción
super_regex = '("#"[^\\n]*\\n)⌕₁|(if)⌕₂|(else)⌕₃|...'
```
- Combina todas las reglas en una expresión regular única
- Añade marcadores únicos para identificar cada token
- Preserva prioridades según orden de definición

#### 3. **Generación de AST y DFA**
- **Conversión a AST**: Utiliza algoritmo Shunting Yard para precedencia de operadores
- **DFA directo**: Implementa construcción directa usando posiciones de hojas
- **Minimización**: Aplica algoritmo de Hopcroft para optimización

#### 4. **Características del Analizador Generado**
- **Reconocimiento de lexema más largo**: Implementa estrategia greedy
- **Manejo de prioridades**: Resuelve conflictos por orden de reglas
- **Eficiencia**: DFA minimizado para rendimiento óptimo

### Formato de Archivos YAL

```yalex
(* ejemplo3.yal *)
{ 
  import myTokens  (* Header opcional *)
}

rule tokens =
    "#"[^\n]*\n              { return COMMENT }
  | "if"                     { return IF }
  | "else"                   { return ELSE }
  | [a-zA-Z_][a-zA-Z0-9_]*   { return ID }
  | [0-9]+                   { return NUMBER }
  | [ \t]+                   { return WHITESPACE }
;

{
  def process_token(token, lexeme):  (* Trailer opcional *)
      return (token, lexeme)
}
```

## YAPar: Generador de Analizadores Sintácticos

### Características Principales

YAPar implementa un generador completo de parsers SLR(1) con las siguientes capacidades:

#### 1. **Análisis de Gramáticas**
- **Parser de archivos .yalp**: Procesa gramáticas en formato BNF extendido
- **Validación sintáctica**: Verifica correctitud de la gramática
- **Manejo de producciones**: Soporta múltiples alternativas por no-terminal

#### 2. **Construcción de Autómatas LR(0)**
```python
# Construcción de colección canónica
def build_lr0_states(productions, start_symbol):
    # Estado inicial con ítem augmentado
    I0 = closure({Item(start_prime, [start_symbol], 0)}, productions)
    states = [I0]
    
    # Construcción iterativa de estados
    for state in states:
        for symbol in grammar_symbols:
            new_state = goto(state, symbol, productions)
            if new_state and new_state not in states:
                states.append(new_state)
```

#### 3. **Cálculo de Conjuntos FIRST y FOLLOW**
- **FIRST**: Determina primeros símbolos de derivaciones
- **FOLLOW**: Calcula símbolos que pueden seguir a un no-terminal
- **Optimización**: Implementación eficiente con punto fijo

#### 4. **Generación de Tablas SLR(1)**
- **Tabla ACTION**: Define acciones shift/reduce/accept para cada estado-terminal
- **Tabla GOTO**: Especifica transiciones para no-terminales
- **Resolución de conflictos**: Utiliza conjuntos FOLLOW para SLR(1)

### Formato de Archivos YALP

```yacc
/* demo.yalp */
%token IF ELSE WHILE ID NUMBER ASSIGN SEMICOLON
%token LPAREN RPAREN LBRACE RBRACE PLUS MINUS

IGNORE WHITESPACE COMMENT

%%

program:
    stmt_list
;

stmt_list:
    stmt_list stmt
  | stmt
;

stmt:
    ID ASSIGN expr SEMICOLON
  | IF LPAREN expr RPAREN stmt
  | LBRACE stmt_list RBRACE
;

expr:
    expr PLUS term
  | expr MINUS term
  | term
;
```

## Pipeline de Orquestación

### Flujo Completo del Sistema

El archivo `pipeline_yalex_yapar.py` implementa la orquestación completa:

```bash
python pipeline_yalex_yapar.py grammar.yal grammar.yalp input.txt
```

#### Fases del Pipeline

1. **Generación del Lexer**
   ```bash
   python -m YALex.app --yal ejemplo3.yal --out thelexer.py
   ```

2. **Generación del Parser**
   ```bash
   python -m YAPar.cli demo.yalp -o theparser.py --visualize
   ```

3. **Análisis Léxico**
   ```python
   import thelexer
   tokens = thelexer.entrypoint(input_text)
   # Output: [('IF', 'if'), ('ID', 'x'), ('ASSIGN', '='), ...]
   ```

4. **Análisis Sintáctico**
   ```python
   import theparser
   result = theparser.parse([tok for tok, _ in tokens])
   # Output: [(0, 'shift IF'), (1, 'reduce expr -> term'), ..., (n, 'accept')]
   ```

5. **Reporte de Resultados**
   - Estado de aceptación/rechazo
   - Detección de errores con contexto
   - Visualizaciones de autómatas

## Instalación y Configuración

### Requisitos

```bash
pip install graphviz
```

### Estructura de Directorios

Asegúrate de que la estructura coincida con la mostrada en [Arquitectura](#arquitectura-del-proyecto).

## Uso Completo del Sistema

### 1. Uso Individual de YALex

```bash
# Generar lexer
cd YALex
python app.py --yal ejemplo3.yal --out thelexer.py

# Usar lexer generado
echo "if x = 5;" | python thelexer.py
# Output: IF if
#         ID x
#         ASSIGN =
#         NUMBER 5
#         SEMICOLON ;
```

### 2. Uso Individual de YAPar

```bash
# Generar parser
cd YAPar
python cli.py examples/demo.yalp -o theparser.py --visualize

# Usar parser generado
echo "ID ASSIGN NUMBER SEMICOLON" | python theparser.py
# Output: 0 shift ID
#         1 shift ASSIGN
#         ...
#         n accept
```

### 3. Uso del Pipeline Completo

```bash
# Análisis completo
python pipeline_yalex_yapar.py YALex/ejemplo3.yal YAPar/examples/demo.yalp input.txt

# Con opciones
python pipeline_yalex_yapar.py \
  --lexer-output mylexer.py \
  --parser-output myparser.py \
  --no-visualize \
  grammar.yal grammar.yalp program.txt
```

### 4. Testing Automatizado

```bash
# Ejecutar suite de pruebas
python script.py

# Test específico
python test_lexer_parser.py input_file.txt
```

## Ejemplos Prácticos

### Ejemplo 1: Lenguaje de Expresiones Aritméticas

**Especificación léxica** (`calc.yal`):
```yalex
rule tokens =
    [0-9]+              { return NUMBER }
  | "+"                 { return PLUS }
  | "-"                 { return MINUS }
  | "*"                 { return TIMES }
  | "/"                 { return DIVIDE }
  | "("                 { return LPAREN }
  | ")"                 { return RPAREN }
  | [ \t\n]+            { return WHITESPACE }
;
```

**Gramática sintáctica** (`calc.yalp`):
```yacc
%token NUMBER PLUS MINUS TIMES DIVIDE LPAREN RPAREN
IGNORE WHITESPACE

%%

expr:
    expr PLUS term
  | expr MINUS term
  | term
;

term:
    term TIMES factor
  | term DIVIDE factor
  | factor
;

factor:
    LPAREN expr RPAREN
  | NUMBER
;
```

**Análisis de entrada**:
```bash
echo "3 + 4 * (2 - 1)" > test.txt
python pipeline_yalex_yapar.py calc.yal calc.yalp test.txt
```

### Ejemplo 2: Subconjunto de C

**Entrada válida**:
```c
if (x > 0) {
    y = x + 1;
    while (y < 10) {
        y = y * 2;
    }
}
```

**Salida del análisis**:
```
✅ ANÁLISIS EXITOSO - El archivo es sintácticamente correcto
Tokens identificados: 23
Acciones de parseo: 45
- Shifts: 23
- Reduces: 21
- Total: 45
```

**Entrada inválida**:
```c
if x > 0 {  // Faltan paréntesis
    y = x +;  // Expresión incompleta
}
```

**Salida del análisis**:
```
❌ ERROR SINTÁCTICO: Token inesperado 'LBRACE' en estado 6

Detalles del error:
- Token rechazado: 'LBRACE'
- Estado del parser: 6
- Posición en tokens: 3

Contexto:
  1: IF 'if'
  2: ID 'x'
  3: GREATER '>'
  4: LBRACE '{' <-- AQUÍ
```

## Detalles Técnicos

### Algoritmos Implementados

#### 1. **Construcción de DFA (YALex)**
- **Método directo**: Evita construcción de AFN intermedio
- **Complejidad**: O(n²) donde n es el tamaño de la expresión regular
- **Optimización**: Minimización con algoritmo de Hopcroft O(n log n)

#### 2. **Construcción LR(0) (YAPar)**
- **Colección canónica**: Enumera todos los estados válidos
- **CLOSURE**: Calcula cierre de conjuntos de ítems
- **GOTO**: Transiciones entre estados por símbolos

#### 3. **Tablas SLR(1)**
```python
# Construcción de tabla ACTION
for state_i, items in enumerate(states):
    for item in items:
        if item.dot < len(item.rhs):  # Shift
            symbol = item.rhs[item.dot]
            if symbol in terminals:
                next_state = goto(items, symbol)
                ACTION[state_i, symbol] = ('shift', next_state)
        else:  # Reduce o Accept
            if item.lhs == augmented_start:
                ACTION[state_i, EOF] = ('accept',)
            else:
                for terminal in FOLLOW[item.lhs]:
                    ACTION[state_i, terminal] = ('reduce', production_index)
```

### Características Avanzadas

#### 1. **Manejo de Errores**
- **Detección precisa**: Identifica token y posición exacta del error
- **Contexto**: Muestra tokens circundantes para debugging
- **Recuperación**: Información para posible recuperación de errores

#### 2. **Visualización**
- **Autómatas DFA**: Diagramas de estados del lexer
- **Autómatas LR(0)**: Visualización de estados y transiciones del parser
- **Formato PDF**: Salida en formato legible y profesional

#### 3. **Optimizaciones**
- **DFA mínimo**: Reduce número de estados para eficiencia
- **Tablas compactas**: Representación eficiente de tablas de parseo
- **Precedencia**: Resolución automática de conflictos shift/reduce

## Testing y Validación

### Suite de Pruebas

El proyecto incluye una batería completa de tests:

```python
# Tests unitarios
pytest YAPar/tests/
pytest YALex/tests/

# Tests de integración
python test_lexer_parser.py

# Tests automatizados con casos válidos e inválidos
python script.py
```

### Casos de Prueba

#### Casos Válidos ✅
- Asignaciones simples: `x = 42;`
- Expresiones aritméticas: `result = 10 + 20 * 3;`
- Estructuras de control: `if (x > 5) { ... }`
- Bloques anidados: `{ { x = 1; } }`

#### Casos Inválidos ❌
- Paréntesis desbalanceados: `x = (5 + 3;`
- Tokens no reconocidos: `x := 5;`
- Sintaxis incorrecta: `x = 5 y = 6;`
- Operadores inválidos: `x = 5 ** 2;`

## Visualización de Resultados

### Archivos Generados

Al ejecutar el sistema completo, se generan varios archivos:

1. **`thelexer.py`**: Analizador léxico independiente
2. **`theparser.py`**: Analizador sintáctico independiente  
3. **`lr0_states.pdf`**: Visualización del autómata LR(0)
4. **`dfa_graph.pdf`**: Visualización del DFA del lexer

### Interpretación de Resultados

#### Análisis Exitoso
```
✅ ANÁLISIS EXITOSO
================================================================================
RESUMEN DE RESULTADOS
================================================================================

Archivos procesados:
  - Especificación léxica: YALex/ejemplo3.yal
  - Especificación sintáctica: YAPar/examples/demo.yalp
  - Archivo de entrada: input.txt

Analizadores generados:
  - Lexer: thelexer.py
  - Parser: theparser.py

Resultados del análisis:
  - Tokens identificados: 25
  - Estado sintáctico: ✅ ACEPTADO
  - Acciones de parseo: 47

Visualizaciones generadas:
  - Autómata LR(0): lr0_states.pdf
```

#### Análisis con Error
```
❌ ERROR SINTÁCTICO: Token inesperado 'SEMICOLON' en estado 12

Detalles del error:
  Token rechazado: 'SEMICOLON'
  Estado del parser: 12
  Posición en tokens: 8

Contexto:
     6: ID 'x'
     7: ASSIGN '='
     8: NUMBER '5'
     9: SEMICOLON ';' <-- AQUÍ
    10: ID 'y'
```

## Destacado

### Características Destacadas

- **Modularidad**: Componentes independientes y reutilizables
- **Eficiencia**: Algoritmos optimizados y estructuras de datos eficientes  
- **Robustez**: Manejo completo de errores con diagnósticos precisos
- **Visualización**: Herramientas gráficas para understanding y debugging
- **Testing**: Suite completa de pruebas automatizadas

### Aplicaciones

El sistema puede utilizarse para:
- Desarrollo de nuevos lenguajes de programación
- Creación de DSLs (Domain Specific Languages)
- Herramientas de análisis de código
- Educación en teoría de compiladores
- Prototipado rápido de sintaxis de lenguajes