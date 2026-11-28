"""
Utilidades compartidas sobre los rituales (funciones) de NecroScrypt.

Las usan tanto el verificador como el generador de código, para que ambos
interpreten el nodo Ritual del ASA exactamente de la misma forma.

Forma del nodo Ritual producida por el Analizador:

    Ritual (contenido = nombre)
        Parametros
            Parametro (contenido = nombre) -> Tipo
        TipoRetorno -> Tipo          (solo si el ritual declara ⚯ tipo)
        Bloque
"""

from Comun import tipos
from Comun.simbolos import RITUAL, Simbolo

# Rituales que el lenguaje ofrece sin que el programador los declare.
# Se identifican porque su símbolo no tiene nodo de declaración (nodo=None)
# y no se les valida la cantidad ni el tipo de los argumentos.
INCORPORADOS = {
    "invocar": Simbolo("invocar", tipos.CENIZA, RITUAL, [], tipos.CENIZA, None),
    "revivir": Simbolo("revivir", tipos.DESCONOCIDO, RITUAL, [], tipos.DESCONOCIDO, None),
}


def es_incorporado(simbolo):
    """
    Indica si un símbolo es uno de los rituales incorporados del lenguaje.

    Parámetros:
        simbolo (Simbolo): Símbolo a consultar, o None.

    Retorna:
        bool: True si es 'invocar' o 'revivir'.
    """
    return simbolo is not None and INCORPORADOS.get(simbolo.nombre) is simbolo


def separar_ritual(nodo):
    """
    Separa las partes de un nodo Ritual.

    Parámetros:
        nodo (NodoASA): Nodo de tipo Ritual.

    Retorna:
        tuple: (parametros, tipo_retorno, bloque) donde parametros es la lista
        de nodos Parametro, tipo_retorno es el nombre del tipo (o None si el
        ritual no declara ⚯) y bloque es el nodo Bloque (o None si falta).
    """
    parametros = []
    tipo_retorno = None
    bloque = None

    for hijo in nodo.hijos:
        if hijo.tipo == "Parametros":
            parametros = list(hijo.hijos)
        elif hijo.tipo == "TipoRetorno" and hijo.hijos:
            tipo_retorno = hijo.hijos[0].contenido
        elif hijo.tipo == "Bloque":
            bloque = hijo

    return parametros, tipo_retorno, bloque


def tipo_de_parametro(parametro):
    """Retorna el nombre del tipo declarado en un nodo Parametro."""
    if parametro.hijos:
        return parametro.hijos[0].contenido
    return tipos.DESCONOCIDO
