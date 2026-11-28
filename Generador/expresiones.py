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

import keyword

from Comun import tipos
from Comun.visitante import Visitante

# Nombres que una variable no puede tener en el Python generado: palabras
# reservadas y funciones que el propio código generado necesita.
NOMBRES_PROTEGIDOS = set(keyword.kwlist) | {
    "print", "input", "str", "int", "float", "bool", "range", "len", "list",
}


def nombre_python(nombre):
    """
    Convierte un identificador de NecroScrypt en uno seguro para Python
    (class -> class_, print -> print_). Todas las partes del generador deben
    usarlo para que una misma variable se traduzca siempre igual.
    """
    if nombre in NOMBRES_PROTEGIDOS:
        return nombre + "_"
    return nombre


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
    
    def es_revivir(self, nodo):
        """True si el nodo es una llamada al ritual incorporado 'revivir'."""
        return (
            nodo is not None
            and nodo.tipo == "LlamadaRitual"
            and nodo.contenido == "revivir"
        )
        
    @staticmethod
    def _cast_input(codigo, tipo_destino):
        """Castea el resultado de revivir (input(), que es str) al tipo destino."""
        if tipo_destino == tipos.CALAVERA:
            return f"int({codigo})"
        if tipo_destino == tipos.ESENCIA:
            return f"float({codigo})"
        if tipo_destino == tipos.LATIDO:
            return f"bool({codigo})"
        return codigo

    def convertir_a(self, nodo, tipo_destino, codigo=None):
        """
        Genera el código de una expresión y aplica la conversión necesaria
        para guardarla en 'tipo_destino':

        - revivir (input()) se castea con int() / float() / bool() según destino.
        - una calavera guardada en una esencia se convierte con float().
        """
        if codigo is None:
            codigo = self.visitar(nodo)
        if self.es_revivir(nodo):
            return self._cast_input(codigo, tipo_destino)
        if tipo_destino == tipos.ESENCIA and nodo.tipo_inferido == tipos.CALAVERA:
            return f"float({codigo})"
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
