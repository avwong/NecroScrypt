"""
ASA construido a mano para comparar contra el que produce el analizador. 
Cada función devuelve el árbol de un ejemplo.
"""
from Analizador.nodo_asa import NodoASA


"""
Genera el texto de atributos de un nodo a partir de su posición.
Argumentos: linea, columna (posición del token que origina el nodo).
Retorna: Cadena con el formato "línea = L, columna = C".
Errores: Ninguno.
"""
def posicion(linea, columna):
    return f"línea = {linea}, columna = {columna}"


"""
Construye a mano el ASA de Explorador/Ejemplos/ejemplo.ns:

    ritual main⟅⟆ ✦
        calavera a <- 20 ☩
        calavera b <- 6 ☩
        cantico nombre <- "Pepe el mago" ☩
        esencia pi <- 3.14 ☩
    ✧

Argumentos: Ninguno.
Retorna: NodoASA raíz (Programa) del ejemplo.
Errores: Ninguno.
"""
def asa_ejemplo():
    bloque = NodoASA("Bloque", "", "", [
        NodoASA("Declaracion", "a", posicion(2, 14), [
            NodoASA("Tipo", "calavera", posicion(2, 5)),
            NodoASA("Entero", "20", posicion(2, 19)),
        ]),
        NodoASA("Declaracion", "b", posicion(3, 14), [
            NodoASA("Tipo", "calavera", posicion(3, 5)),
            NodoASA("Entero", "6", posicion(3, 19)),
        ]),
        NodoASA("Declaracion", "nombre", posicion(4, 13), [
            NodoASA("Tipo", "cantico", posicion(4, 5)),
            NodoASA("Cadena", "Pepe el mago", posicion(4, 23)),
        ]),
        NodoASA("Declaracion", "pi", posicion(5, 13), [
            NodoASA("Tipo", "esencia", posicion(5, 5)),
            NodoASA("Decimal", "3.14", posicion(5, 19)),
        ]),
    ])

    ritual = NodoASA("Ritual", "main", posicion(1, 8), [
        NodoASA("Parametros"),
        bloque,
    ])

    return NodoASA("Programa", "", "", [ritual])


if __name__ == "__main__":
    asa_ejemplo().imprimir()
