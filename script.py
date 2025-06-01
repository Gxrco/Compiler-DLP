
"""
Script de demostración del pipeline YALex + YAPar
Incluye casos de prueba con archivos válidos e inválidos
"""

import os
import sys
import subprocess
import tempfile

# Configurar colores para la salida
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")

def run_test(name, yal_file, yalp_file, input_content, expected_result="accept"):
    """Ejecuta una prueba del pipeline completo"""
    print(f"\n{Colors.OKBLUE}Prueba: {name}{Colors.ENDC}")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(input_content)
        input_file = f.name
    
    try:
        # Ejecutar el pipeline
        result = subprocess.run(
            [sys.executable, "pipeline_yalex_yapar.py", 
             yal_file, yalp_file, input_file],
            capture_output=True,
            text=True
        )
        
        # Verificar resultado
        if expected_result == "accept":
            if "✅ ANÁLISIS EXITOSO" in result.stdout:
                print(f"{Colors.OKGREEN}✅ PASÓ: El archivo fue aceptado como se esperaba{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.FAIL}❌ FALLÓ: Se esperaba aceptación pero fue rechazado{Colors.ENDC}")
                print(f"Salida:\n{result.stdout[-500:]}")  # Últimos 500 caracteres
                return False
        else:
            if "❌ ERROR SINTÁCTICO" in result.stdout or "❌ ANÁLISIS FALLIDO" in result.stdout:
                print(f"{Colors.OKGREEN}✅ PASÓ: El archivo fue rechazado como se esperaba{Colors.ENDC}")
                # Mostrar el error detectado
                error_lines = [line for line in result.stdout.split('\n') 
                              if 'Token inesperado' in line or 'Token rechazado' in line]
                if error_lines:
                    print(f"{Colors.WARNING}   Error detectado: {error_lines[0]}{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.FAIL}❌ FALLÓ: Se esperaba rechazo pero fue aceptado{Colors.ENDC}")
                return False
                
    finally:
        # Limpiar archivo temporal
        os.unlink(input_file)

def create_test_files():
    """Crea archivos de prueba temporales si no existen"""
    # Crear una gramática simple de prueba si no existe demo.yalp
    if not os.path.exists("YAPar/examples/demo_corregido.yalp"):
        print(f"{Colors.WARNING}Creando archivo de gramática de prueba...{Colors.ENDC}")
        os.makedirs("YAPar/examples", exist_ok=True)
        with open("YAPar/examples/demo_corregido.yalp", "w") as f:
            f.write("""/* Gramática simple de prueba */
%token IF ELSE WHILE ID NUMBER ASSIGN SEMICOLON
%token LPAREN RPAREN LBRACE RBRACE
%token PLUS MINUS TIMES DIVIDE
%token EQUALS NOTEQUAL LESS GREATER

IGNORE WHITESPACE COMMENT

%%

program:
    statement_list
;

statement_list:
    statement_list statement
  | statement
;

statement:
    ID ASSIGN expression SEMICOLON
  | IF LPAREN expression RPAREN statement
  | LBRACE statement_list RBRACE
;

expression:
    expression PLUS term
  | expression MINUS term
  | term
;

term:
    term TIMES factor
  | term DIVIDE factor
  | factor
;

factor:
    LPAREN expression RPAREN
  | ID
  | NUMBER
;
""")

def main():
    print_header("DEMOSTRACIÓN DEL PIPELINE YALex + YAPar")
    
    # Verificar que existe el script principal
    if not os.path.exists("pipeline_yalex_yapar.py"):
        print(f"{Colors.FAIL}Error: No se encuentra pipeline_yalex_yapar.py{Colors.ENDC}")
        print("Asegúrate de haber guardado el archivo del pipeline primero.")
        sys.exit(1)
    
    # Archivos de especificación
    yal_file = "YALex/ejemplo3.yal"
    yalp_file = "YAPar/examples/demo_corregido.yalp"
    
    # Verificar que existen los archivos necesarios
    if not os.path.exists(yal_file):
        print(f"{Colors.FAIL}Error: No se encuentra {yal_file}{Colors.ENDC}")
        sys.exit(1)
    
    create_test_files()
    
    # Casos de prueba
    test_cases = [
        # Casos válidos
        ("Asignación simple", 
         "x = 42;", 
         "accept"),
        
        ("Expresión aritmética", 
         "result = 10 + 20 * 3;", 
         "accept"),
        
        ("Bloque con múltiples statements", 
         """{ 
             x = 5;
             y = x + 1;
             z = x * y;
         }""", 
         "accept"),
        
        # Casos inválidos
        ("Paréntesis desbalanceados", 
         "x = (5 + 3;", 
         "reject"),
        
        ("Token no reconocido", 
         "x := 5;",  # := no está definido en la gramática
         "reject"),
        
        ("Sintaxis incorrecta - falta semicolon", 
         "x = 5 y = 6;", 
         "reject"),
        
        ("Operador inválido",
         "x = 5 ** 2;",  # ** no está definido
         "reject"),
        
        ("Estructura if incompleta",
         "if x > 5",  # Falta paréntesis y cuerpo
         "reject"),
    ]
    
    # Ejecutar pruebas
    passed = 0
    failed = 0
    
    print(f"\n{Colors.OKCYAN}Ejecutando {len(test_cases)} casos de prueba...{Colors.ENDC}")
    
    for name, input_content, expected in test_cases:
        if run_test(name, yal_file, yalp_file, input_content, expected):
            passed += 1
        else:
            failed += 1
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    print(f"\nTotal de pruebas: {len(test_cases)}")
    print(f"{Colors.OKGREEN}Pasadas: {passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}Fallidas: {failed}{Colors.ENDC}")
    
    if failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}¡Todas las pruebas pasaron exitosamente!{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}Algunas pruebas fallaron. Revisa los detalles arriba.{Colors.ENDC}")
    
    # Información adicional sobre archivos generados
    print(f"\n{Colors.OKCYAN}Archivos generados:{Colors.ENDC}")
    for file in ["thelexer.py", "theparser.py", "lr0_states.pdf"]:
        if os.path.exists(file):
            print(f"  ✓ {file}")
    
    print(f"\n{Colors.OKCYAN}Para ver el autómata LR(0), abre: lr0_states.pdf{Colors.ENDC}")

if __name__ == "__main__":
    main()