#!/usr/bin/env python3
"""
Pipeline completo YALex + YAPar
Orquesta la generación y ejecución de analizadores léxicos y sintácticos
"""

import sys
import os
import subprocess
import argparse
import importlib.util
from typing import List, Tuple, Optional
import traceback

class CompilerPipeline:
    def __init__(self, yal_file: str, yalp_file: str, input_file: str, 
                 lexer_output: str = "thelexer.py", 
                 parser_output: str = "theparser.py",
                 visualize: bool = True):
        self.yal_file = yal_file
        self.yalp_file = yalp_file
        self.input_file = input_file
        self.lexer_output = lexer_output
        self.parser_output = parser_output
        self.visualize = visualize
        self.tokens = []
        self.parse_result = []
        
        # Configurar el path para importar módulos de YALex
        self._setup_python_path()
    
    def _setup_python_path(self):
        """Añade YALex al path de Python para encontrar chain_compiler y afd_compiler"""
        yalex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "YALex")
        if yalex_dir not in sys.path:
            sys.path.insert(0, yalex_dir)
    
    def run(self):
        """Ejecuta el pipeline completo"""
        print("="*80)
        print("PIPELINE COMPLETO: YALex + YAPar")
        print("="*80)
        
        # Paso 1: Generar el lexer
        if not self._generate_lexer():
            return False
        
        # Paso 2: Generar el parser
        if not self._generate_parser():
            return False
        
        # Paso 3: Leer archivo de entrada
        input_text = self._read_input_file()
        if input_text is None:
            return False
        
        # Paso 4: Tokenizar con el lexer
        if not self._tokenize(input_text):
            return False
        
        # Paso 5: Parsear con el parser
        if not self._parse():
            return False
        
        # Paso 6: Generar visualización del autómata LR(0)
        if self.visualize:
            self._visualize_lr0()
        
        # Paso 7: Mostrar resumen de resultados
        self._show_summary()
        
        return True
    
    def _generate_lexer(self) -> bool:
        """Genera el analizador léxico usando YALex"""
        print(f"\n1. GENERACIÓN DEL ANALIZADOR LÉXICO")
        print(f"   Archivo YAL: {self.yal_file}")
        print(f"   Salida: {self.lexer_output}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "YALex.app", 
                 "--yal", self.yal_file, 
                 "--out", self.lexer_output],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"   ❌ Error: {result.stderr}")
                return False
            
            print(f"   ✅ Lexer generado exitosamente")
            return True
            
        except Exception as e:
            print(f"   ❌ Error al generar lexer: {e}")
            return False
    
    def _generate_parser(self) -> bool:
        """Genera el analizador sintáctico usando YAPar"""
        print(f"\n2. GENERACIÓN DEL ANALIZADOR SINTÁCTICO")
        print(f"   Archivo YALP: {self.yalp_file}")
        print(f"   Salida: {self.parser_output}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "YAPar.cli", 
                 self.yalp_file, 
                 "-o", self.parser_output],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"   ❌ Error: {result.stderr}")
                return False
            
            # Extraer información sobre la gramática
            if "Tokens declarados:" in result.stdout:
                tokens_part = result.stdout.split('Tokens declarados:')[1]
                first_line = tokens_part.split('\n')[0]
                print(f"   {first_line}")
            if "estados LR(0) generados" in result.stdout:
                estados_info = [line for line in result.stdout.split('\n') 
                               if "estados LR(0) generados" in line]
                if estados_info:
                    print(f"   {estados_info[0]}")
            
            print(f"   ✅ Parser generado exitosamente")
            return True
            
        except Exception as e:
            print(f"   ❌ Error al generar parser: {e}")
            return False
    
    def _read_input_file(self) -> Optional[str]:
        """Lee el archivo de entrada a analizar"""
        print(f"\n3. LECTURA DEL ARCHIVO DE ENTRADA")
        print(f"   Archivo: {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"   Tamaño: {len(content)} caracteres")
            print(f"   Primeras líneas:")
            for i, line in enumerate(content.split('\n')[:3]):
                print(f"      {i+1}: {line}")
            
            return content
            
        except FileNotFoundError:
            print(f"   ❌ Error: Archivo no encontrado")
            return None
        except Exception as e:
            print(f"   ❌ Error al leer archivo: {e}")
            return None
    
    def _tokenize(self, input_text: str) -> bool:
        """Tokeniza el texto de entrada usando el lexer generado"""
        print(f"\n4. ANÁLISIS LÉXICO")
        
        try:
            # Importar el lexer generado
            spec = importlib.util.spec_from_file_location("thelexer", self.lexer_output)
            lexer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lexer_module)
            
            # Tokenizar
            self.tokens = lexer_module.entrypoint(input_text)
            
            print(f"   Tokens generados: {len(self.tokens)}")
            print(f"   Primeros tokens:")
            for i, (tok, lex) in enumerate(self.tokens[:10]):
                print(f"      {i+1:3d}: {tok:15} '{lex}'")
            
            if len(self.tokens) > 10:
                print(f"      ... y {len(self.tokens)-10} tokens más")
            
            # Verificar si hay tokens de error
            error_tokens = [(i, tok, lex) for i, (tok, lex) in enumerate(self.tokens) 
                           if tok == "ERROR"]
            
            if error_tokens:
                print(f"\n   ⚠️  Se encontraron {len(error_tokens)} errores léxicos:")
                for i, tok, lex in error_tokens[:5]:
                    print(f"      Posición {i}: '{lex}'")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error durante tokenización: {e}")
            traceback.print_exc()
            return False
    
    def _parse(self) -> bool:
        """Parsea los tokens usando el parser generado"""
        print(f"\n5. ANÁLISIS SINTÁCTICO")
        
        try:
            # Importar el parser generado
            spec = importlib.util.spec_from_file_location("theparser", self.parser_output)
            parser_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(parser_module)
            
            # Extraer solo los nombres de tokens
            token_names = [tok for tok, _ in self.tokens]
            
            print(f"   Parseando {len(token_names)} tokens...")
            
            # Parsear
            self.parse_result = parser_module.parse(token_names)
            
            # Mostrar resumen de acciones
            shift_count = sum(1 for _, action in self.parse_result if "shift" in action)
            reduce_count = sum(1 for _, action in self.parse_result if "reduce" in action)
            
            print(f"   Acciones realizadas:")
            print(f"      Shifts: {shift_count}")
            print(f"      Reduces: {reduce_count}")
            print(f"      Total: {len(self.parse_result)}")
            
            # Verificar si se llegó a accept
            if self.parse_result and self.parse_result[-1][1] == 'accept':
                print(f"\n   ✅ ANÁLISIS EXITOSO - El archivo es sintácticamente correcto")
                return True
            else:
                print(f"\n   ❌ ANÁLISIS FALLIDO - No se llegó al estado de aceptación")
                # Mostrar últimas acciones para debug
                print(f"   Últimas acciones:")
                for state, action in self.parse_result[-5:]:
                    print(f"      Estado {state}: {action}")
                return False
                
        except Exception as e:
            print(f"\n   ❌ ERROR SINTÁCTICO: {e}")
            
            # Intentar identificar el token problemático
            if "Token inesperado" in str(e):
                error_msg = str(e)
                # Extraer información del error
                import re
                match = re.search(r"Token inesperado '(\w+)' en estado (\d+)", error_msg)
                if match:
                    bad_token = match.group(1)
                    bad_state = match.group(2)
                    
                    # Encontrar posición del token en la entrada
                    token_pos = -1
                    for i, (tok, _) in enumerate(self.tokens):
                        if tok == bad_token:
                            token_pos = i
                            break
                    
                    print(f"\n   Detalles del error:")
                    print(f"      Token rechazado: '{bad_token}'")
                    print(f"      Estado del parser: {bad_state}")
                    
                    if token_pos >= 0:
                        print(f"      Posición en tokens: {token_pos}")
                        # Mostrar contexto
                        print(f"      Contexto:")
                        start = max(0, token_pos - 2)
                        end = min(len(self.tokens), token_pos + 3)
                        for i in range(start, end):
                            tok, lex = self.tokens[i]
                            marker = " <-- AQUÍ" if i == token_pos else ""
                            print(f"         {i}: {tok} '{lex}'{marker}")
            
            return False
    
    def _visualize_lr0(self):
        """Genera visualización del autómata LR(0)"""
        print(f"\n6. VISUALIZACIÓN DEL AUTÓMATA LR(0)")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "YAPar.cli", 
                 self.yalp_file, 
                 "-o", "theparser.py",
                 "--visualize"],
                capture_output=True,
                text=True
            )
            
            if "lr0_states.pdf" in result.stdout:
                print(f"   ✅ Autómata LR(0) generado: lr0_states.pdf")
            else:
                print(f"   ⚠️  No se pudo generar la visualización")
                
        except Exception as e:
            print(f"   ⚠️  Error al generar visualización: {e}")
    
    def _show_summary(self):
        """Muestra un resumen de los resultados"""
        print(f"\n{'='*80}")
        print("RESUMEN DE RESULTADOS")
        print(f"{'='*80}")
        
        print(f"\nArchivos procesados:")
        print(f"  - Especificación léxica: {self.yal_file}")
        print(f"  - Especificación sintáctica: {self.yalp_file}")
        print(f"  - Archivo de entrada: {self.input_file}")
        
        print(f"\nAnalizadores generados:")
        print(f"  - Lexer: {self.lexer_output}")
        print(f"  - Parser: {self.parser_output}")
        
        print(f"\nResultados del análisis:")
        print(f"  - Tokens identificados: {len(self.tokens)}")
        
        if self.parse_result:
            if self.parse_result[-1][1] == 'accept':
                print(f"  - Estado sintáctico: ✅ ACEPTADO")
                print(f"  - Acciones de parseo: {len(self.parse_result)}")
            else:
                print(f"  - Estado sintáctico: ❌ RECHAZADO")
                print(f"  - Acciones antes del error: {len(self.parse_result)}")
        else:
            print(f"  - Estado sintáctico: ❌ ERROR")
        
        if self.visualize and os.path.exists("lr0_states.pdf"):
            print(f"\nVisualizaciones generadas:")
            print(f"  - Autómata LR(0): lr0_states.pdf")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline completo YALex + YAPar para análisis léxico y sintáctico"
    )
    
    parser.add_argument(
        "yal_file",
        help="Archivo .yal con especificación léxica"
    )
    
    parser.add_argument(
        "yalp_file", 
        help="Archivo .yalp con especificación sintáctica"
    )
    
    parser.add_argument(
        "input_file",
        help="Archivo de entrada a analizar"
    )
    
    parser.add_argument(
        "--lexer-output", "-l",
        default="thelexer.py",
        help="Nombre del archivo de salida para el lexer (default: thelexer.py)"
    )
    
    parser.add_argument(
        "--parser-output", "-p",
        default="theparser.py",
        help="Nombre del archivo de salida para el parser (default: theparser.py)"
    )
    
    parser.add_argument(
        "--no-visualize",
        action="store_true",
        help="No generar visualización del autómata LR(0)"
    )
    
    args = parser.parse_args()
    
    # Verificar que los archivos existan
    for file_path, file_type in [(args.yal_file, "YAL"), 
                                  (args.yalp_file, "YALP"), 
                                  (args.input_file, "entrada")]:
        if not os.path.exists(file_path):
            print(f"Error: No se encuentra el archivo {file_type}: {file_path}")
            sys.exit(1)
    
    # Ejecutar el pipeline
    pipeline = CompilerPipeline(
        yal_file=args.yal_file,
        yalp_file=args.yalp_file,
        input_file=args.input_file,
        lexer_output=args.lexer_output,
        parser_output=args.parser_output,
        visualize=not args.no_visualize
    )
    
    success = pipeline.run()
    
    # Retornar código de salida apropiado
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()