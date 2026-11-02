"""
Manejo centralizado de errores para el compilador/transpilador NecroScrypt.

Define una jerarquía limpia de errores para las fases del compilador:
- ErrorLexico: generado por el Explorador.
- ErrorSintactico: generado por el Analizador.
- GestorErrores: recolector y organizador de diagnósticos.
"""


class ErrorCompilacion:
    """
    Clase base para cualquier error ocurrido durante la compilación/transpilación.

    Guarda la fase donde ocurrió, la línea, la columna y el mensaje descriptivo.
    """

    def __init__(self, fase, linea, columna, mensaje):
        self.fase = str(fase)
        self.linea = int(linea)
        self.columna = int(columna)
        self.mensaje = str(mensaje)
        self.es_correcto = False

    def __contains__(self, texto_buscado):
        """Permite verificar si un texto está contenido en el mensaje de error."""
        return texto_buscado in str(self)

    def __str__(self):
        return f"Error {self.fase} en línea {self.linea}, columna {self.columna}: {self.mensaje}"

    def __repr__(self):
        return f"<{self.__class__.__name__}: L{self.linea}:C{self.columna} - {self.mensaje}>"


class ErrorLexico(ErrorCompilacion):
    """
    Representa un error léxico detectado por el Explorador (Scanner).
    Por ejemplo: un carácter inválido, un número mal formado o una cadena sin cerrar.
    """

    def __init__(self, token, linea, columna, mensaje="Token incorrecto", codigo_error=None):
        super().__init__("léxico", linea, columna, mensaje)
        # Limpiar el texto del token para que no tenga saltos de línea innecesarios
        if isinstance(token, str):
            self.token = token.strip()
        else:
            self.token = token
        self.codigo_error = codigo_error

    def __str__(self):
        return f"Error lexico: {self.mensaje} '{self.token}' en linea {self.linea}, columna {self.columna}"

    def __repr__(self):
        return f"<ErrorLexico: '{self.token}' en L{self.linea}:C{self.columna}>"


class ErrorSintactico(str):
    """
    Representa un error sintáctico detectado por el Analizador (Parser).
    Hereda de str para ser 100% compatible con cualquier código o prueba que
    espere una cadena con formato: 'Línea X: Se esperaba 'A', pero encontré 'B'',
    pero a la vez ofrece propiedades estructuradas (.linea, .columna, .esperado, .encontrado).
    """

    fase: str
    linea: int
    columna: int
    mensaje: str
    esperado: str | None
    encontrado: str | None
    es_correcto: bool

    def __new__(cls, linea, columna, esperado=None, encontrado=None, mensaje=None):
        if mensaje is None and esperado is not None and encontrado is not None:
            texto_cuerpo = f"Se esperaba '{esperado}', pero encontré '{encontrado}'"
        elif mensaje is not None:
            texto_cuerpo = mensaje
        else:
            texto_cuerpo = "Error de sintaxis"

        cadena_completa = f"Línea {linea}: {texto_cuerpo}"
        instancia = super().__new__(cls, cadena_completa)
        instancia.fase = "sintáctico"
        instancia.linea = int(linea)
        instancia.columna = int(columna)
        instancia.mensaje = texto_cuerpo
        instancia.esperado = esperado
        instancia.encontrado = encontrado
        instancia.es_correcto = False
        return instancia

    def __repr__(self):
        return f"<ErrorSintactico: Línea {self.linea}, Columna {self.columna}: {self.mensaje}>"


class GestorErrores:
    """
    Colecciona y organiza los errores producidos durante todo el proceso
    de compilación o transpilación.
    """

    def __init__(self):
        self.errores = []

    def registrar(self, error):
        """Agrega un nuevo error al gestor."""
        self.errores.append(error)

    def hay_errores(self):
        """Retorna True si hay al menos un error registrado."""
        return len(self.errores) > 0

    def obtener_por_fase(self, nombre_fase):
        """Retorna todos los errores pertenecientes a una fase dada ('léxico', 'sintáctico')."""
        resultado = []
        for err in self.errores:
            fase = getattr(err, "fase", "")
            if fase.lower() == nombre_fase.lower():
                resultado.append(err)
        return resultado

    def imprimir_resumen(self):
        """Muestra en la consola todos los errores agrupados por fase."""
        if not self.hay_errores():
            print("No se encontraron errores.")
            return

        errores_lexicos = self.obtener_por_fase("léxico")
        if len(errores_lexicos) > 0:
            print(f"Se encontraron {len(errores_lexicos)} errores lexicos:\n")
            for err in errores_lexicos:
                print(f"  - {err}")
            print()

        errores_sintacticos = self.obtener_por_fase("sintáctico")
        if len(errores_sintacticos) > 0:
            print(f"Se encontraron {len(errores_sintacticos)} errores sintacticos:\n")
            for err in errores_sintacticos:
                print(f"  - {err}")
            print()
