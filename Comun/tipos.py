"""
Reglas del sistema de tipos de NecroScrypt.

Centraliza los nombres de los tipos y las reglas de compatibilidad para que
el verificador y el generador de código usen exactamente las mismas.

Tipos primitivos:
    calavera  -> entero          (int en Python)
    esencia   -> decimal         (float en Python)
    cantico   -> texto           (str en Python)
    latido    -> booleano        (bool en Python)
    ceniza    -> vacío / nulo    (None en Python)

Tipos compuestos:
    fosa <primitivo>  -> lista homogénea (list en Python)
"""

CALAVERA = "calavera"
ESENCIA = "esencia"
CANTICO = "cantico"
LATIDO = "latido"
CENIZA = "ceniza"

PREFIJO_FOSA = "fosa"

# Tipo de una fosa vacía ☾☽: es compatible con cualquier fosa
FOSA_VACIA = "fosa"

# Tipo de una expresión cuyo tipo no se pudo determinar (por ejemplo, una
# variable no declarada). Se acepta en cualquier operación para no generar
# errores en cascada: el error original ya lo reporta quien lo detectó.
DESCONOCIDO = "desconocido"

NUMERICOS = (CALAVERA, ESENCIA)

# Operadores del lenguaje agrupados por categoría
OPERADORES_ARITMETICOS = ("ensamblar", "mutilar", "infestar", "desmembrar", "restos")
OPERADORES_IGUALDAD = ("==", "!=")
OPERADORES_ORDEN = ("<", ">", "<=", ">=")
OPERADORES_LOGICOS = ("y", "o")


def es_numerico(tipo):
    """Indica si el tipo es calavera o esencia."""
    return tipo in NUMERICOS


def es_fosa(tipo):
    """Indica si el tipo es una fosa (lista)."""
    return tipo is not None and tipo.split(" ")[0] == PREFIJO_FOSA


def tipo_fosa(tipo_elemento):
    """Construye el tipo de una fosa a partir del tipo de sus elementos."""
    return f"{PREFIJO_FOSA} {tipo_elemento}"


def es_compatible(tipo_destino, tipo_origen):
    """
    Indica si un valor de tipo_origen puede guardarse en algo de tipo_destino
    (asignaciones, declaraciones, retornos y paso de argumentos).

    Reglas:
        - Mismo tipo: compatible.
        - calavera se promueve a esencia (se convierte con float()).
        - Una fosa vacía cabe en cualquier fosa.
        - Un tipo desconocido no genera errores en cascada.
    """
    if DESCONOCIDO in (tipo_destino, tipo_origen):
        return True
    if tipo_destino == tipo_origen:
        return True
    if tipo_destino == ESENCIA and tipo_origen == CALAVERA:
        return True
    if es_fosa(tipo_destino) and tipo_origen == FOSA_VACIA:
        return True
    return False


def tipo_aritmetico(operador, izquierdo, derecho):
    """
    Calcula el tipo resultante de una operación aritmética.

    Reglas:
        - calavera (op) calavera -> calavera (desmembrar es división entera).
        - Si alguno es esencia   -> esencia.
        - cantico ensamblar cantico -> cantico (concatenación).
        - Cualquier otra combinación es inválida.

    Retorna:
        str: Tipo resultante, o None si la operación no es válida.
    """
    if DESCONOCIDO in (izquierdo, derecho):
        return DESCONOCIDO
    if es_numerico(izquierdo) and es_numerico(derecho):
        if izquierdo == CALAVERA and derecho == CALAVERA:
            return CALAVERA
        return ESENCIA
    if operador == "ensamblar" and izquierdo == CANTICO and derecho == CANTICO:
        return CANTICO
    return None


def tipo_comparacion(operador, izquierdo, derecho):
    """
    Calcula el tipo resultante de una comparación.

    Reglas:
        - == y != : mismos tipos, números entre sí, o cualquier cosa contra ceniza.
        - < > <= >= : números entre sí o canticos entre sí.

    Retorna:
        str: LATIDO si es válida, o None si no lo es.
    """
    if DESCONOCIDO in (izquierdo, derecho):
        return LATIDO
    if es_numerico(izquierdo) and es_numerico(derecho):
        return LATIDO
    if operador in OPERADORES_IGUALDAD:
        if izquierdo == derecho or CENIZA in (izquierdo, derecho):
            return LATIDO
        return None
    if izquierdo == CANTICO and derecho == CANTICO:
        return LATIDO
    return None


def tipo_logico(izquierdo, derecho):
    """
    Calcula el tipo resultante de 'y' / 'o'. Ambos lados deben ser latido.

    Retorna:
        str: LATIDO si es válida, o None si no lo es.
    """
    validos = (LATIDO, DESCONOCIDO)
    if izquierdo in validos and derecho in validos:
        return LATIDO
    return None
