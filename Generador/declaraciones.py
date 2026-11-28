"""
Generación de código Python para las declaraciones de variables de NecroScrypt.

GeneradorDeclaraciones es un visitante pensado para combinarse por herencia
con GeneradorExpresiones (necesita su método convertir_a) y con GeneradorBase,
en Generador/generador.py.

    calavera a <- 20 ☩        ->   a = 20
    esencia pi <- 3 ☩         ->   pi = float(3)
    fosa cantico n <- ☾☽ ☩    ->   n = []
"""

from Comun import tipos
from Generador.expresiones import nombre_python

# Valor que toma una variable cuando la declaración no trae valor inicial
VALORES_POR_DEFECTO = {
    tipos.CALAVERA: "0",
    tipos.ESENCIA: "0.0",
    tipos.CANTICO: '""',
    tipos.LATIDO: "False",
    tipos.CENIZA: "None",
}


def valor_por_defecto(tipo):
    """
    Retorna el código Python del valor inicial por defecto de un tipo.

    Parámetros:
        tipo (str): Tipo declarado ('calavera', 'fosa cantico', ...).

    Retorna:
        str: '[]' para las fosas, o el valor del tipo primitivo ('None' si no se conoce).
    """
    if tipos.es_fosa(tipo):
        return "[]"
    return VALORES_POR_DEFECTO.get(tipo, "None")


class GeneradorDeclaraciones:
    """Traduce las declaraciones del ASA decorado a código Python 3.8+."""

    def visitar_Declaracion(self, nodo):
        """
        Tipo nombre <- valor ☩   ->   nombre = valor

        Si la declaración no trae valor inicial se usa el valor por defecto del
        tipo. Una calavera guardada en una esencia se convierte con float().
        """
        tipo_declarado = nodo.hijos[0].contenido
        if len(nodo.hijos) > 1:
            valor = self.convertir_a(nodo.hijos[1], tipo_declarado)
        else:
            valor = valor_por_defecto(tipo_declarado)
        return f"{nombre_python(nodo.contenido)} = {valor}"
