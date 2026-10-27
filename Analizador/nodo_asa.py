"""
Nodo del Árbol de Sintaxis Abstracto (ASA) de NecroScrypt.
"""


class NodoASA:
    """Representa un nodo del ASA con su tipo, contenido, atributos e hijos."""

    """
    Crea el nodo
    Argumentos: tipo (nombre del tipo de nodo, ej: "Declaracion"),
                contenido (texto del nodo, ej: el nombre de una variable),
                atributos (texto con línea y columna, o vacío),
                hijos (lista opcional de nodos hijo).
    Retorna: Nada.
    Errores: Ninguno.
    """
    def __init__(self, tipo, contenido="", atributos="", hijos=None):
        self.tipo = tipo
        self.contenido = contenido
        self.atributos = atributos
        self.hijos = list(hijos) if hijos else []

    """
    Crea un nodo tomando la posición de un token del explorador.
    Argumentos: tipo (tipo de nodo), token (Token que origina el nodo),
                contenido (opcional, si no se da se usa el del token).
    Retorna: El nuevo nodo, con atributos "línea = L, columna = C".
    Errores: Ninguno.
    """
    @classmethod
    def desde_token(cls, tipo, token, contenido=None):
        if contenido is None:
            contenido = token.contenido
        atributos = f"línea = {token.linea}, columna = {token.columna}"
        return cls(tipo, contenido, atributos)

    """
    Agrega un nodo hijo al final de la lista de hijos.
    Argumentos: nodo (nodo hijo).
    Retorna: El nodo hijo agregado, o None si nodo es None.
    Errores: Ninguno.
    """
    def agregar_hijo(self, nodo):
        if nodo is None:
            return None

        self.hijos.append(nodo)
        return nodo

    """
    Genera el formato de una línea del nodo: <"Tipo", "Contenido", "Atributos">
    Argumentos: Ninguno.
    Retorna: Cadena con el formato del nodo (sin sus hijos).
    Errores: Ninguno.
    """
    def __repr__(self):
        return f'<"{self.tipo}", "{self.contenido}", "{self.atributos}">'

    """
    Recorre el árbol en preorden (nodo, luego sus hijos de izquierda a derecha).
    Argumentos: sangria (si es True, indenta cada línea según su profundidad),
                nivel (profundidad del nodo, se usa en la recursión).
    Retorna: Lista de cadenas, una por nodo, en formato <"Tipo", "Contenido", "Atributos">.
    Errores: Ninguno.
    """
    def preorden(self, sangria=True, nivel=0):
        prefijo = "  " * nivel if sangria else ""
        lineas = [prefijo + repr(self)]
        for hijo in self.hijos:
            lineas.extend(hijo.preorden(sangria, nivel + 1))
        return lineas

    """
    Genera el texto del árbol completo, un nodo por línea en preorden.
    Argumentos: sangria (si es True, indenta cada línea según su profundidad).
    Retorna: Cadena con el árbol, útil para compararlo en pruebas.
    Errores: Ninguno.
    """
    def a_texto(self, sangria=True):
        return "\n".join(self.preorden(sangria))

    """
    Imprime el árbol completo en consola, un nodo por línea en preorden.
    Argumentos: sangria (si es True, indenta cada línea según su profundidad).
    Retorna: Nada.
    Errores: Ninguno.
    """
    def imprimir(self, sangria=True):
        print(self.a_texto(sangria))
