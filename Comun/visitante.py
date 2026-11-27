"""
Clase base del patrón Visitante para recorrer el ASA de NecroScrypt.

El recorrido es descendente (Top-Down): el visitante entra primero al nodo
padre y desde ahí decide cuándo y cómo visitar a sus hijos.

Cada fase que recorre el árbol (verificador, generador de código, impresor)
hereda de Visitante y define un método por cada tipo de nodo que le interesa:

    class MiVisitante(Visitante):
        def visitar_Declaracion(self, nodo):
            ...

El nombre del método se forma como "visitar_" + nodo.tipo. Si un tipo de nodo
no tiene método propio, se usa visitar_generico, que solo recorre a los hijos.
"""


class Visitante:
    """Despacha cada nodo del ASA al método visitar_<Tipo> correspondiente."""

    PREFIJO = "visitar_"

    def visitar(self, nodo):
        """
        Visita un nodo llamando al método específico de su tipo.

        Parámetros:
            nodo (NodoASA): Nodo a visitar. Si es None se ignora.

        Retorna:
            Lo que retorne el método específico (un tipo, código, etc.).
        """
        if nodo is None:
            return None
        metodo = getattr(self, self.PREFIJO + nodo.tipo, self.visitar_generico)
        return metodo(nodo)

    def visitar_hijos(self, nodo):
        """
        Visita a todos los hijos de un nodo de izquierda a derecha.

        Retorna:
            list: Resultados de visitar cada hijo, en el mismo orden.
        """
        return [self.visitar(hijo) for hijo in nodo.hijos]

    def visitar_generico(self, nodo):
        """
        Comportamiento por defecto para nodos sin método propio: recorrer
        a los hijos en preorden y no producir ningún resultado.
        """
        self.visitar_hijos(nodo)
        return None
