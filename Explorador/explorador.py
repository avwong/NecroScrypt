"""
Explorador Léxico (Scanner) para NecroScrypt.

Recorre el código fuente carácter por carácter, reconociendo tokens
(palabras clave, identificadores, números, operadores) y recuperándose
de caracteres desconocidos mediante Modo Pánico.
"""

from Comun.errores import ErrorLexico
from Comun.gramatica import (
    operadores_dobles,
    palabras_reservadas,
    simbolos,
    tokens_seguros,
)
from Comun.tokens import Token


class Explorador:
    """
    Analizador léxico secuencial y amigable para principiantes.
    """

    def __init__(self, codigo_fuente):
        self.fuente = codigo_fuente
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.inicio_linea = 1
        self.inicio_columna = 1
        self.tokens = []
        self.errores = []

    # -------------------------------------------------------------------------
    # Navegación del cursor
    # -------------------------------------------------------------------------

    def es_letra(self, caracter):
        """Comprueba si un carácter es una letra de la A a la Z."""
        if caracter is None:
            return False
        es_minuscula = ('a' <= caracter <= 'z')
        es_mayuscula = ('A' <= caracter <= 'Z')
        return es_minuscula or es_mayuscula

    def es_digito(self, caracter):
        """Comprueba si un carácter es un dígito del 0 al 9."""
        if caracter is None:
            return False
        return '0' <= caracter <= '9'

    def actual(self):
        """Carácter actual sin mover la posición (None al llegar al final)."""
        if self.posicion < len(self.fuente):
            return self.fuente[self.posicion]
        return None

    def siguiente(self):
        """Carácter inmediatamente siguiente sin mover la posición."""
        posicion_siguiente = self.posicion + 1
        if posicion_siguiente < len(self.fuente):
            return self.fuente[posicion_siguiente]
        return None

    def mirar_adelante(self, longitud):
        """Lee una ventana de texto hacia adelante sin mover el cursor."""
        return self.fuente[self.posicion:self.posicion + longitud]

    def avanzar(self) -> str:
        """
        Avanza el cursor un carácter y actualiza número de línea y columna.
        Retorna el carácter leído como cadena, o cadena vacía "" si ya llegó al final.
        """
        if self.posicion < len(self.fuente):
            caracter_leido = self.fuente[self.posicion]
            self.posicion += 1

            if caracter_leido == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1

            return caracter_leido
        return ""

    def marcar_inicio(self):
        """Guarda la posición exacta donde inicia el token."""
        self.inicio_linea = self.linea
        self.inicio_columna = self.columna

    def agregar(self, tipo, contenido, atributo=""):
        """Construye un nuevo objeto Token y lo agrega a la lista de tokens."""
        if atributo != "":
            texto_atributo = f"{atributo}, línea = {self.inicio_linea}, columna = {self.inicio_columna}"
        else:
            texto_atributo = f"línea = {self.inicio_linea}, columna = {self.inicio_columna}"

        nuevo_token = Token(
            tipo=tipo,
            contenido=contenido,
            linea=self.inicio_linea,
            columna=self.inicio_columna,
            atributo=texto_atributo
        )
        self.tokens.append(nuevo_token)

    def registrar_error(self, token_invalido, mensaje="Token incorrecto"):
        """Registra un ErrorLexico con la ubicación de inicio."""
        nuevo_error = ErrorLexico(
            token=token_invalido,
            linea=self.inicio_linea,
            columna=self.inicio_columna,
            mensaje=mensaje
        )
        self.errores.append(nuevo_error)

    def modo_panico(self):
        """Descarta caracteres inválidos hasta encontrar un delimitador seguro."""
        texto_descartado = ""
        while self.actual() is not None and self.actual() not in tokens_seguros:
            texto_descartado += self.avanzar()
        return texto_descartado

    # -------------------------------------------------------------------------
    # Rutinas de escaneo especializadas
    # -------------------------------------------------------------------------

    def escanear_comentario(self):
        """Lee un comentario completo delimitado entre '~~' y '~~'."""
        texto = self.avanzar() + self.avanzar()  # Consume los dos '~' iniciales

        while True:
            # Error si la línea o el archivo terminan sin cerrar el comentario
            if self.actual() is None or self.actual() == '\n':
                self.registrar_error(texto, mensaje="Comentario sin cerrar")
                return

            # Cierre exitoso con '~~'
            if self.actual() == '~' and self.siguiente() == '~':
                texto += self.avanzar()
                texto += self.avanzar()
                self.agregar("COMENTARIO", texto)
                return

            texto += self.avanzar()

    def escanear_cadena(self):
        """Lee una cadena de texto entre comillas dobles (ejemplo: "Hola")."""
        texto = self.avanzar()  # Consume la comilla inicial '"'

        while True:
            # Error si la línea o el archivo terminan sin cerrar la comilla
            if self.actual() is None or self.actual() == '\n':
                self.registrar_error(texto, mensaje="Cadena sin cerrar")
                return

            # Cierre exitoso con '"'
            if self.actual() == '"':
                texto += self.avanzar()
                contenido_sin_comillas = texto[1:-1]
                self.agregar("CADENA", texto, contenido_sin_comillas)
                return

            texto += self.avanzar()

    def escanear_numero(self):
        """
        Lee números enteros o decimales (por ejemplo: 20 o 3.14).

        Paso 1: Acumula los dígitos de la parte entera.
        Paso 2: Si hay un punto '.', valida si viene seguido de dígitos decimales.
        Paso 3: Si hay errores (más de un punto como 1.5.0 o letras pegadas como 1a),
                activa el modo pánico y registra el error.
        Paso 4: Guarda el Token como 'ENTERO' o 'DECIMAL'.
        """
        texto = ""
        while self.es_digito(self.actual()):
            texto += self.avanzar()

        es_decimal = False

        # Paso 2: Revisar si hay un punto decimal
        if self.actual() == '.':
            # Verificar si el carácter después del punto es un dígito
            if self.es_digito(self.siguiente()):
                es_decimal = True
                texto += self.avanzar()  # Consume el punto '.'
                while self.es_digito(self.actual()):
                    texto += self.avanzar()
            else:
                # Punto sin dígitos a la derecha (ejemplo: '3.')
                descarte = self.modo_panico()
                texto_invalido = texto + descarte
                self.registrar_error(texto_invalido)
                return

        # Paso 3: Revisar si viene otro punto (ej: 1.5.0) o letras/guion bajo pegados (ej: 1a)
        tiene_otro_punto = (self.actual() == '.')
        tiene_letras_pegadas = self.es_letra(self.actual()) or (self.actual() == '_')

        if tiene_otro_punto or tiene_letras_pegadas:
            descarte = self.modo_panico()
            texto_invalido = texto + descarte
            self.registrar_error(texto_invalido)
            return

        # Paso 4: Determinar el tipo de token de forma explícita
        if es_decimal:
            tipo_numero = "DECIMAL"
        else:
            tipo_numero = "ENTERO"

        self.agregar(tipo_numero, texto, texto)

    def escanear_identificador(self):
        """
        Lee nombres de variables, palabras reservadas o el caso compuesto 'sin mana'.
        """
        texto = ""
        while self.actual() is not None and (
            self.es_letra(self.actual()) or
            self.es_digito(self.actual()) or
            self.actual() == '_'
        ):
            texto += self.avanzar()

        # Caso especial para la palabra clave compuesta de dos términos: 'sin mana'
        if texto == "sin":
            pos_inicial = self.posicion
            lin_inicial = self.linea
            col_inicial = self.columna

            # Leer espacios intermedios en blanco
            while self.actual() in [' ', '\t']:
                self.avanzar()

            sigue_palabra_mana = (self.mirar_adelante(4) == "mana")
            caracter_despues = self.fuente[self.posicion + 4:self.posicion + 5]
            es_otra_palabra = (
                self.es_letra(caracter_despues) or
                self.es_digito(caracter_despues) or
                caracter_despues == '_'
            )

            if sigue_palabra_mana and not es_otra_palabra:
                # Avanzar los 4 caracteres de 'mana'
                for _ in range(4):
                    self.avanzar()
                texto = "sin mana"
            else:
                # Restaurar cursor si no era la palabra 'mana'
                self.posicion = pos_inicial
                self.linea = lin_inicial
                self.columna = col_inicial

        # Buscar si es palabra reservada o un identificador normal
        if texto in palabras_reservadas:
            tipo_token = palabras_reservadas[texto]
        else:
            tipo_token = "IDENTIFICADOR"

        self.agregar(tipo_token, texto)

    # -------------------------------------------------------------------------
    # Bucle principal
    # -------------------------------------------------------------------------

    def escanear(self):
        """Recorre todo el texto fuente y retorna la lista de Tokens reconocidos."""
        while self.actual() is not None:
            caracter = self.actual()

            # 1. Ignorar espacios en blanco y saltos de línea
            if caracter in [' ', '\t', '\r', '\n']:
                self.avanzar()
                continue

            self.marcar_inicio()

            # 2. Comentarios (inician con '~~')
            if caracter == '~' and self.siguiente() == '~':
                self.escanear_comentario()
                continue

            # 3. Cadenas de texto entre comillas (inician con '"')
            if caracter == '"':
                self.escanear_cadena()
                continue

            # 4. Números enteros o decimales
            if self.es_digito(caracter):
                self.escanear_numero()
                continue

            # 5. Identificadores y palabras reservadas
            if self.es_letra(caracter):
                self.escanear_identificador()
                continue

            # 6. Operadores de dos caracteres (<- , <= , >= , == , !=)
            dos_caracteres = self.mirar_adelante(2)
            if dos_caracteres in operadores_dobles:
                self.avanzar()
                self.avanzar()
                self.agregar(operadores_dobles[dos_caracteres], dos_caracteres)
                continue

            # 7. Símbolos individuales y operadores de un carácter
            if caracter in simbolos:
                self.avanzar()
                self.agregar(simbolos[caracter], caracter)
                continue

            # 8. Carácter desconocido -> Modo Pánico para recuperarse
            descarte = self.modo_panico()
            self.registrar_error(descarte)

        return self.tokens
