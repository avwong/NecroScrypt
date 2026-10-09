# Manejo de errores lexicos para NecroScrypt

class ErrorLexico:
    """
    Representa un error lexico en NecroScrypt.
    Indica de forma directa si un token es incorrecto y su ubicacion.
    """
    def __init__(self, token, linea, columna, mensaje="Token incorrecto"):
        self.token = token.strip() if isinstance(token, str) else token
        self.linea = linea
        self.columna = columna
        self.mensaje = mensaje
        self.es_correcto = False

    def __str__(self):
        return f"Error lexico: {self.mensaje} '{self.token}' en linea {self.linea}, columna {self.columna}"

    def __repr__(self):
        return f"<ErrorLexico: '{self.token}' en L{self.linea}:C{self.columna}>"
