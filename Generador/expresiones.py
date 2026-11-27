"""
Generación de código Python para las expresiones y asignaciones de NecroScrypt.

GeneradorExpresiones es un visitante pensado para combinarse por herencia con
el resto del generador (declaraciones, rituales, estructuras de control):

    class GeneradorPython(GeneradorExpresiones, GeneradorInstrucciones, ...):
        ...

Requiere que el ASA ya esté decorado por el verificador (tipo_inferido),
porque algunas traducciones dependen del tipo: la división de dos calaveras
es entera (//) y una calavera guardada en una esencia se convierte con float().

Cada método visitar_<Expresion> retorna un str con código Python válido.
visitar_Asignacion retorna una línea sin sangría; la sangría la agrega quien
arma los bloques.
"""

from Comun import tipos
from Comun.visitante import Visitante
from Generador.nombres import nombre_python

OPERADORES_PYTHON = {
    "ensamblar": "+",
    "mutilar": "-",
    "infestar": "*",
    "restos": "%",
    "y": "and",
    "o": "or",
    "==": "==",
    "!=": "!=",
    "<": "<",
    ">": ">",
    "<=": "<=",
    ">=": ">=",
}

# Nodos binarios: cuando aparecen como operando se encierran entre paréntesis
# para conservar exactamente la agrupación del ASA.
NODOS_BINARIOS = ("OperacionAritmetica", "Comparacion", "OperacionLogica")

BOOLEANOS = {"vivo": "True", "muerto": "False"}


class GeneradorExpresiones(Visitante):
    """Traduce expresiones del ASA decorado a código Python 3.8+."""

    def visitar_generico(self, nodo):
        raise NotImplementedError(
            f"El generador no tiene traducción para el nodo '{nodo.tipo}'"
        )

    # ------------------------------------------------------------------
    # Literales
    # ------------------------------------------------------------------

    def visitar_Entero(self, nodo):
        # int() elimina ceros a la izquierda (007), que Python no acepta
        return str(int(nodo.contenido))

    def visitar_Decimal(self, nodo):
        return nodo.contenido

    def visitar_Cadena(self, nodo):
        # repr() produce un literal de Python válido y escapa lo necesario
        return repr(nodo.contenido)

    def visitar_Booleano(self, nodo):
        return BOOLEANOS[nodo.contenido]

    def visitar_Ceniza(self, nodo):
        return "None"

    def visitar_Lista(self, nodo):
        elementos = [self.visitar(hijo) for hijo in nodo.hijos]
        if nodo.tipo_inferido == tipos.tipo_fosa(tipos.ESENCIA):
            elementos = [
                self.convertir_a(hijo, tipos.ESENCIA, codigo)
                for hijo, codigo in zip(nodo.hijos, elementos)
            ]
        return "[" + ", ".join(elementos) + "]"

    def visitar_Identificador(self, nodo):
        return nombre_python(nodo.contenido)

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------

    def visitar_OperacionAritmetica(self, nodo):
        if nodo.contenido == "desmembrar":
            # calavera desmembrar calavera es división entera
            operador = "//" if nodo.tipo_inferido == tipos.CALAVERA else "/"
        else:
            operador = OPERADORES_PYTHON[nodo.contenido]
        return self.generar_binaria(nodo, operador)

    def visitar_Comparacion(self, nodo):
        return self.generar_binaria(nodo, OPERADORES_PYTHON[nodo.contenido])

    def visitar_OperacionLogica(self, nodo):
        return self.generar_binaria(nodo, OPERADORES_PYTHON[nodo.contenido])

    def generar_binaria(self, nodo, operador):
        izquierdo, derecho = nodo.hijos[0], nodo.hijos[1]
        return f"{self.generar_operando(izquierdo)} {operador} {self.generar_operando(derecho)}"

    def generar_operando(self, nodo):
        """Genera un operando, con paréntesis si es a su vez una operación."""
        codigo = self.visitar(nodo)
        if nodo.tipo in NODOS_BINARIOS:
            return f"({codigo})"
        return codigo

    # ------------------------------------------------------------------
    # Conversiones de tipo
    # ------------------------------------------------------------------

    def convertir_a(self, nodo, tipo_destino, codigo=None):
        """
        Genera el código de una expresión convertido explícitamente al tipo
        destino cuando hace falta.

        Conversiones:
            calavera -> esencia : float(x)
            * -> cantico        : str(x); los latido se muestran como
                                  vivo/muerto y la ceniza como "ceniza".

        Parámetros:
            nodo: Expresión decorada con tipo_inferido.
            tipo_destino (str): Tipo que se necesita.
            codigo (str, opcional): Código ya generado del nodo.

        Retorna:
            str: Código Python de la expresión ya convertida.
        """
        if codigo is None:
            codigo = self.visitar(nodo)
        tipo_origen = nodo.tipo_inferido

        if tipo_origen == tipo_destino or tipo_origen in (None, tipos.DESCONOCIDO):
            return codigo
        if tipo_destino == tipos.ESENCIA and tipo_origen == tipos.CALAVERA:
            return f"float({codigo})"
        if tipo_destino == tipos.CANTICO:
            if tipo_origen == tipos.LATIDO:
                return f'("vivo" if {codigo} else "muerto")'
            if tipo_origen == tipos.CENIZA:
                return '"ceniza"'
            return f"str({codigo})"
        return codigo

    # ------------------------------------------------------------------
    # Instrucciones
    # ------------------------------------------------------------------

    def visitar_Asignacion(self, nodo):
        """
        x <- expresion ☩   ->   x = expresion

        El verificador deja en nodo.tipo_inferido el tipo de la variable, para
        aplicar la conversión necesaria (por ejemplo, float() en esencias).
        """
        valor = self.convertir_a(nodo.hijos[0], nodo.tipo_inferido)
        return f"{nombre_python(nodo.contenido)} = {valor}"
