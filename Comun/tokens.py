"""
Definición de Tokens para NecroScrypt.

Un Token representa la unidad básica de información que produce el Explorador Léxico (Scanner),
como por ejemplo un número, una palabra reservada o un símbolo.
"""


class Token:
    """
    Representa una palabra, número o símbolo reconocido en el código fuente.

    Guarda:
    - tipo: Qué categoría es (ejemplo: 'CALAVERA', 'ENTERO', 'ASIGNACION').
    - contenido: El texto exacto tal como se escribió en el código fuente.
    - linea: Número de línea donde inicia el token (comienza en 1).
    - columna: Número de columna donde inicia el token (comienza en 1).
    - atributo: Información extra útil, como el valor semántico o la posición.
    """

    def __init__(self, tipo, contenido, linea, columna, atributo=""):
        self.tipo = tipo
        self.contenido = str(contenido)
        self.linea = int(linea)
        self.columna = int(columna)
        self.atributo = str(atributo)
        self.es_correcto = True

    def __repr__(self):
        """
        Formato de texto estándar para visualizar un Token en consola:
        <"Tipo" | "Contenido" | "Linea" | "Columna" | "Atributo">
        """
        return (
            f'<"{self.tipo}" | "{self.contenido}" | '
            f'"{self.linea}" | "{self.columna}" | "{self.atributo}">'
        )

    def __str__(self):
        return self.__repr__()
