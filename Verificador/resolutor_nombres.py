"""
Resolución de nombres de NecroScrypt.

Recorre una expresión y, para cada identificador y cada llamada a ritual,
busca su declaración en la tabla de símbolos. Deja la referencia directa en
nodo.simbolo_ref y reporta los errores de nombres:

    - variable o ritual no declarado
    - cantidad incorrecta de argumentos al invocar un ritual

No calcula tipos: eso lo hace la inferencia de tipos una vez resueltos los
nombres.
"""

from Comun.rituales import es_incorporado
from Comun.simbolos import RITUAL
from Comun.visitante import Visitante


class ResolutorNombres(Visitante):
    """
    Visitante que decora identificadores y llamadas con su símbolo.

    Parámetros:
        tabla (TablaSimbolos): Tabla donde se buscan y reportan los nombres.
    """

    def __init__(self, tabla):
        self.tabla = tabla

    def visitar_Identificador(self, nodo):
        """Busca la variable en la tabla y la deja en nodo.simbolo_ref."""
        self.tabla.resolver(nodo)

    def visitar_LlamadaRitual(self, nodo):
        """
        Resuelve primero los argumentos (pueden contener otras llamadas) y
        luego el ritual invocado, validando la cantidad de argumentos.
        """
        self.visitar_hijos(nodo)
        simbolo = self.tabla.resolver(nodo, es_llamada=True)
        self.validar_cantidad_argumentos(nodo, simbolo)

    def validar_cantidad_argumentos(self, nodo, simbolo):
        """
        Compara los argumentos recibidos con los parámetros del ritual.
        Los rituales incorporados (invocar, revivir) aceptan cualquier cantidad.
        """
        if simbolo is None or simbolo.categoria != RITUAL or es_incorporado(simbolo):
            return

        argumentos = nodo.hijos[0].hijos if nodo.hijos else []
        esperados = len(simbolo.parametros)
        if len(argumentos) != esperados:
            self.tabla.reportar(
                nodo,
                f"El ritual '{nodo.contenido}' espera {esperados} argumento(s), "
                f"pero recibió {len(argumentos)}",
            )
