"""
Transpilador de NecroScrypt.

Punto de entrada principal que orquesta las primeras fases del compilador/transpilador:
  1. Fase Léxica: El Explorador (Scanner) lee el archivo .ns y produce tokens.
  2. Fase Sintáctica: El Analizador (Parser) verifica la gramática y construye el ASA.
  3. Manejo de Errores: Informa claramente cualquier error léxico o sintáctico detectado.
"""

import sys

from Analizador.analizador import Analizador
from Explorador.explorador import Explorador


def procesar_archivo(ruta_archivo):
    """
    Lee un archivo de código fuente NecroScrypt (.ns), realiza el análisis
    léxico y sintáctico, y muestra los tokens reconocidos y el árbol generado.

    Argumentos:
        ruta_archivo (str): Ruta al archivo con extensión .ns.

    Retorna:
        list: Lista de tokens reconocidos, o None si ocurre un error de lectura.
    """
    
    # 1. Validar que la extensión sea .ns
    if not ruta_archivo.endswith(".ns"):
        print("Error: El archivo no termina en .ns, no es un archivo de Necroscrypt.")
        return None

    # 2. Leer el contenido del archivo de texto
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            fuente = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontro el archivo '{ruta_archivo}'.")
        return None

    # 3. Fase 1: Análisis Léxico (Explorador / Scanner)
    explorador = Explorador(fuente)
    tokens = explorador.escanear()

    # Informar si se encontraron errores léxicos
    if len(explorador.errores) > 0:
        print(f"Se encontraron {len(explorador.errores)} errores lexicos:\n")
        for err in explorador.errores:
            print(f"  - {err}")
        print()

    # 4. Fase 2: Análisis Sintáctico Analizador
    analizador = Analizador(tokens)
    asa = analizador.analizar()

    # Informar si se encontraron errores sintácticos
    if len(analizador.errores) > 0:
        print(f"Se encontraron {len(analizador.errores)} errores sintacticos:\n")
        for err in analizador.errores:
            print(f"  - {err}")
        print()

    # 5. Mostrar el Árbol de Sintaxis Abstracta (ASA) resultante
    print("Árbol de Sintaxis Abstracta (ASA):")
    asa.imprimir()

    return tokens


if __name__ == "__main__":
    # Comprobar que el usuario proporcione el archivo como argumento en la terminal
    if len(sys.argv) != 2:
        print("Uso: python transpilador.py <archivo.ns>")
    else:
        procesar_archivo(sys.argv[1])
