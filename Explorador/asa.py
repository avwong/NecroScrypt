

class Token:
    """Representa un token reconocido con su tipo, contenido y posición."""

    """
    Crea un nuevo token con toda su información
    Argumentos: tipo, contenido, linea, columna, atributo (opcional)
    Retorna: Nada.
    Errores: Ninguno.
    """
    def __init__(self, tipo, contenido, linea, columna, atributo=""):
        self.tipo = tipo
        self.contenido = contenido
        self.linea = linea
        self.columna = columna
        self.atributo = atributo
        self.es_correcto = True

    """
    Genera el formato en texto para imprimir el token en consola, como __str__
    Argumentos: Ninguno.
    Retorna: Cadena con el formato del token.
    Errores: Ninguno.
    """
    def __repr__(self):
        return f'<"{self.tipo}" | "{self.contenido}" | "{self.linea}" | "{self.columna}" | "{self.atributo}">'


class NodoASA:
    """Representa un nodo del Árbol de Sintaxis Abstracto."""

    """
    Crea el nodo
    Argumentos: etiqueta (tipo de nodo), componente (token opcional).
    Retorna: Nada.
    Errores: Ninguno.
    """
    def __init__(self, etiqueta, componente=None):
        self.Token
        self.hijos = []

    """
    Agrega un nodo hijo
    Argumentos: nodo (nodo hijo).
    Retorna: El nodo hijo agregado.
    Errores: Que no exista el nodo, pero ni esta el error
    """
    def agregar_hijo(self, nodo):
        if not nodo:
            return

        self.hijos.append(nodo)
        return nodo
