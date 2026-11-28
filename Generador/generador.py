"""
Generador de código Python de NecroScrypt.

Recorre el ASA ya decorado por el verificador con el patrón Visitante y
produce un archivo .py que se puede ejecutar con Python 3.8 o superior.

GeneradorPython combina por herencia las partes del generador. Cada parte
define los métodos visitar_<Nodo> de un grupo de nodos:

    GeneradorRituales      rituales, retornos y llamadas
    GeneradorDeclaraciones declaraciones de variables
    GeneradorExpresiones   expresiones y asignaciones
    GeneradorBase          salida, sangría, programa y ensamblado
"""

import os

from Generador.base import GeneradorBase
from Generador.declaraciones import GeneradorDeclaraciones
from Generador.expresiones import GeneradorExpresiones
from Generador.rituales import GeneradorRituales
from Generador.control import GeneradorControl


class GeneradorPython(
    GeneradorRituales,
    GeneradorDeclaraciones,
    GeneradorExpresiones,
    GeneradorControl,
    GeneradorBase,
):
    """Generador completo: traduce un ASA decorado a código Python 3.8+."""

def ruta_salida(ruta_fuente):
    """
    Calcula la ruta del archivo Python a partir de la del código fuente.

    Parámetros:
        ruta_fuente (str): Ruta del archivo .ns.

    Retorna:
        str: La misma ruta con extensión .py (ejemplo.ns -> ejemplo.py).
    """
    return os.path.splitext(ruta_fuente)[0] + ".py"


def escribir_archivo(ruta, codigo):
    """
    Escribe el código generado en un archivo .py (UTF-8, saltos de línea \\n).

    Parámetros:
        ruta (str): Ruta del archivo de salida.
        codigo (str): Código Python a escribir.
    """
    with open(ruta, "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(codigo)
