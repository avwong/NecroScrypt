

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
