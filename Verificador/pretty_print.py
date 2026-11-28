"""
PrettyPrintVisitor: imprime el ASA decorado en pre-orden.

Por cada nodo emite DOS líneas:

    <"Tipo", "contenido", "atributos">      <- estructura sintáctica
      ↳ decorado                            <- atributos semánticos

La segunda línea muestra tipo_inferido y símbolo_ref (si los hay) para
separar visualmente lo que vino del parser de lo que añadió el verificador.

El recorrido es en pre-orden (padre antes que hijos). La indentación crece
con la profundidad del árbol.
"""

from Comun.visitante import Visitante


class PrettyPrintVisitor(Visitante):
    """
    Recorre el ASA decorado e imprime estructura + atributos semánticos.

    Parámetros:
        salida (callable): Función usada para imprimir (por defecto print).
    """

    SEPARADOR_DECORADO = "  ↳ "

    def __init__(self, salida=print):
        self.salida = salida

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def imprimir(self, asa):
        """Imprime el ASA completo en pre-orden."""
        self._imprimir_nodo(asa, 0)

    def visitar(self, nodo):
        """Compatibilidad con el patrón Visitante (imprime desde la raíz dada)."""
        self.imprimir(nodo)
        return None

    def visitar_generico(self, nodo):
        # No se usa: el recorrido lo hace _imprimir_nodo directamente.
        return None

    # ------------------------------------------------------------------
    # Recorrido
    # ------------------------------------------------------------------

    def _imprimir_nodo(self, nodo, profundidad):
        if nodo is None:
            return
        sangria = "  " * profundidad
        self.salida(f'{sangria}<"{nodo.tipo}", "{nodo.contenido}", "{nodo.atributos}">')
        self.salida(f"{sangria}{self.SEPARADOR_DECORADO}{self._describir_decorados(nodo)}")
        for hijo in nodo.hijos:
            self._imprimir_nodo(hijo, profundidad + 1)

    # ------------------------------------------------------------------
    # Descripción de los decorados
    # ------------------------------------------------------------------

    def _describir_decorados(self, nodo):
        partes = []
        if nodo.tipo_inferido is not None:
            partes.append(f"tipo_inferido = {nodo.tipo_inferido}")
        simbolo = nodo.simbolo_ref
        if simbolo is not None:
            partes.append(self._describir_simbolo(simbolo))
        if not partes:
            return "(sin decorar)"
        return " · ".join(partes)

    @staticmethod
    def _describir_simbolo(simbolo):
        texto = f"símbolo = {simbolo.categoria} '{simbolo.nombre}'"
        if simbolo.nodo is not None:
            linea, _ = simbolo.nodo.posicion()
            if linea:
                texto += f" (línea {linea})"
        return texto