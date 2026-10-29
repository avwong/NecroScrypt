from Explorador.explorador import Explorador
from Analizador.analizador import Analizador


def procesar_archivo(ruta_archivo):
    """Lee un .ns, escanea, parsea y muestra tokens + ASA."""
    if not ruta_archivo.endswith(".ns"):
        print("Error: El archivo no termina en .ns, no es un archivo de Necroscrypt.")
        return None

    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            fuente = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontro el archivo '{ruta_archivo}'.")
        return None

    explorador = Explorador(fuente)
    tokens = explorador.escanear()

    if explorador.errores:
        print(f"Se encontraron {len(explorador.errores)} errores lexicos:\n")
        for err in explorador.errores:
            print(f"  - {err}")
        print()

    print(f"Tokens reconocidos ({len(tokens)}):")
    for tok in tokens:
        print(tok)
    print()

    # ---- Análisis sintáctico ----
    analizador = Analizador(tokens)
    
    asa = analizador.analizar()
    

    if analizador.errores:
        print(f"Se encontraron {len(analizador.errores)} errores sintacticos:\n")
        for err in analizador.errores:
            print(f"  - {err}")
        print()

    print("Árbol de Sintaxis Abstracta (ASA):")
    asa.imprimir()
    return tokens


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python transpilador.py <archivo.ns>")
    else:
        procesar_archivo(sys.argv[1])