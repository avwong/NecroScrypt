"""
Transpilador de NecroScrypt.

Punto de entrada principal que orquesta las primeras fases del compilador/transpilador:
  1. Fase Léxica: El Explorador (Scanner) lee el archivo .ns y produce tokens.
  2. Fase Sintáctica: El Analizador (Parser) verifica la gramática y construye el ASA.
  3. Fase Semántica: El Verificador revisa nombres y tipos, y decora el ASA.
  4. Generación de Código: El Generador traduce el ASA decorado a un archivo .py.
  5. Manejo de Errores: Informa claramente cualquier error detectado en cada fase.
"""

import sys

from Analizador.analizador import Analizador
from Explorador.explorador import Explorador
from Generador.generador import GeneradorPython, escribir_archivo, ruta_salida
from Verificador.verificador import Verificador


def verificar_asa(asa):
    """
    Fase 3: verifica nombres y tipos del ASA y lo decora con las referencias
    a los símbolos y los tipos inferidos. Imprime la tabla de símbolos cada
    vez que cambia y los errores semánticos al final.

    Argumentos:
        asa (NodoASA): Raíz del árbol producido por el analizador.

    Retorna:
        Verificador: El verificador, con sus errores y su tabla de símbolos.
    """
    print("Tabla de símbolos:")
    verificador = Verificador()
    verificador.verificar(asa)

    if len(verificador.errores) > 0:
        print(f"\nSe encontraron {len(verificador.errores)} errores semanticos:\n")
        for err in verificador.errores:
            print(f"  - {err}")
        print()
    return verificador


def generar_codigo(asa, tabla, ruta_archivo):
    """
    Fase 4: traduce el ASA decorado a Python y escribe el archivo .py junto
    al archivo fuente.

    Argumentos:
        asa (NodoASA): Raíz del árbol ya verificado.
        tabla (TablaSimbolos): Tabla de símbolos del verificador.
        ruta_archivo (str): Ruta del archivo .ns de origen.

    Retorna:
        str: Ruta del archivo .py generado, o None si no se pudo generar.
    """
    try:
        codigo = GeneradorPython(tabla).generar(asa)
    except NotImplementedError as error:
        print(f"Error: no se pudo generar el código. {error}")
        return None

    ruta_python = ruta_salida(ruta_archivo)
    escribir_archivo(ruta_python, codigo)
    print(f"Código Python generado en '{ruta_python}'.")
    return ruta_python


def procesar_archivo(ruta_archivo):
    """
    Lee un archivo de código fuente NecroScrypt (.ns), realiza el análisis
    léxico y sintáctico, verifica el árbol y genera el archivo Python de salida.

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

    # 6. Fases 3 y 4: solo se continúa si el código no tiene errores previos
    if len(explorador.errores) > 0 or len(analizador.errores) > 0:
        print("No se verifica ni se genera código mientras haya errores léxicos o sintácticos.")
        return tokens

    verificador = verificar_asa(asa)
    if len(verificador.errores) == 0:
        generar_codigo(asa, verificador.tabla, ruta_archivo)

    return tokens


if __name__ == "__main__":
    # Comprobar que el usuario proporcione el archivo como argumento en la terminal
    if len(sys.argv) != 2:
        print("Uso: python transpilador.py <archivo.ns>")
    else:
        procesar_archivo(sys.argv[1])
