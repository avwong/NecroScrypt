"""
Traducción de identificadores de NecroScrypt a nombres válidos de Python.

Un programa NecroScrypt puede usar nombres que en Python son palabras
reservadas (if, class, def...) o funciones que el código generado necesita
(print, str, float...). Esos nombres se renombran agregando un "_" al final.

Todas las partes del generador (declaraciones, rituales, expresiones) deben
usar nombre_python() para que una misma variable se traduzca siempre igual.
"""

import keyword

# Funciones de Python que el código generado utiliza y que no deben quedar
# ocultas por una variable del programa con el mismo nombre.
FUNCIONES_USADAS_POR_EL_GENERADOR = {
    "print", "input", "str", "int", "float", "bool", "range", "len", "list",
}

NOMBRES_PROTEGIDOS = set(keyword.kwlist) | FUNCIONES_USADAS_POR_EL_GENERADOR


def nombre_python(nombre):
    """
    Convierte un identificador de NecroScrypt en uno seguro para Python.

    Ejemplos:
        vida   -> vida
        class  -> class_
        print  -> print_
    """
    if nombre in NOMBRES_PROTEGIDOS:
        return nombre + "_"
    return nombre
