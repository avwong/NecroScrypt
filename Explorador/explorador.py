"""
Explorador Léxico (Scanner) para NecroScrypt.
Lee el código fuente caracter por caracter, reconoce tokens y detecta errores léxicos.
"""
from asa import Token
from errores import ErrorLexico
from gramatica import operadores_dobles, palabras_reservadas, simbolos, tokens_seguros


class Explorador:
    """Analizador léxico que recorre el texto y lo divide en tokens."""

    """
    Prepara el explorador para empezar a leer el texto fuente.
    Argumentos: fuente (código a escanear como texto).
    Retorna: Nada.
    Errores: Ninguno.
    """
    def __init__(self, fuente):
        self.fuente = fuente
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.inicio_linea = 1
        self.inicio_columna = 1
        self.tokens = []
        self.errores = []

    """
    Revisa si un caracter es una letra de la A a la Z.
    Argumentos: caracter (caracter a revisar o None).
    Retorna: True si es letra, False en caso contrario.
    Errores: Ninguno.
    """
    def es_letra(self, caracter):
        return caracter is not None and ('a' <= caracter <= 'z' or 'A' <= caracter <= 'Z')

    """
    Revisa si un caracter es un dígito del 0 al 9.
    Argumentos: caracter (caracter a revisar o None).
    Retorna: True si es dígito, False en caso contrario.
    Errores: Ninguno.
    """
    def es_digito(self, caracter):
        return caracter is not None and ('0' <= caracter <= '9')

    """
    Retorna el caracter en la posición actual sin avanzar.
    Argumentos: Ninguno.
    Retorna: El caracter actual o None si terminó el texto.
    Errores: Ninguno.
    """
    def actual(self):
        if self.posicion < len(self.fuente):
            return self.fuente[self.posicion]
        return None

    """
    Mira el caracter que sigue sin mover la posición actual.
    Argumentos: Ninguno.
    Retorna: El siguiente caracter o None si no hay más.
    Errores: Ninguno.
    """
    def siguiente(self):
        futura_pos = self.posicion + 1
        if futura_pos < len(self.fuente):
            return self.fuente[futura_pos]
        return None

    """
    Lee el caracter actual, avanza una posición y actualiza línea y columna.
    Argumentos: Ninguno.
    Retorna: El caracter leído o None si llegó al final.
    Errores: Ninguno.
    """
    def avanzar(self):
        if self.posicion < len(self.fuente):
            caracter = self.fuente[self.posicion]
            self.posicion += 1
            if caracter == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            return caracter
        return None

    """
    Guarda la línea y columna exactas donde empieza el token actual.
    Argumentos: Ninguno.
    Retorna: Nada.
    Errores: Ninguno.
    """
    def marcar_inicio(self):
        self.inicio_linea = self.linea
        self.inicio_columna = self.columna

    """
    Crea un nuevo Token y lo añade a la lista de tokens reconocidos.
    Argumentos: tipo, contenido, atributo (opcional).
    Retorna: Nada.
    Errores: Ninguno.
    """
    def agregar(self, tipo, contenido, atributo=""):
        if atributo:
            texto_atributo = f"{atributo}, línea = {self.inicio_linea}, columna = {self.inicio_columna}"
        else:
            texto_atributo = f"línea = {self.inicio_linea}, columna = {self.inicio_columna}"

        token = Token(tipo, contenido, self.inicio_linea, self.inicio_columna, texto_atributo)
        self.tokens.append(token)

    """
    Crea un ErrorLexico y lo guarda en la lista de errores.
    Argumentos: token_invalido (texto con error), mensaje (descripción del fallo).
    Retorna: Nada.
    Errores: Registra el error léxico con su ubicación de inicio.
    """
    def registrar_error(self, token_invalido, mensaje="Token incorrecto"):
        error = ErrorLexico(token_invalido, self.inicio_linea, self.inicio_columna, mensaje)
        self.errores.append(error)

    """
    Descarta caracteres inválidos hasta llegar a un token seguro o fin de texto.
    Argumentos: Ninguno.
    Retorna: Cadena con el texto descartado durante la recuperación.
    Errores: Ninguno.
    """
    def modo_panico(self):
        descartado = ""
        while self.actual() is not None and self.actual() not in tokens_seguros:
            descartado += self.avanzar()
        return descartado

    """
    Lee un comentario completo desde '~~' hasta su cierre '~~'.
    Argumentos: Ninguno.
    Retorna: Nada.
    Errores: Registra error si el comentario no cierra antes del fin de línea o archivo.
    """
    def escanear_comentario(self):
        texto = self.avanzar() + self.avanzar()  # Consume los dos '~' iniciales

        while True:
            # Si se acaba la línea o el archivo sin cerrar el comentario
            if self.actual() is None or self.actual() == '\n':
                self.registrar_error(texto, mensaje="Comentario sin cerrar")
                return

            # Si encontramos el cierre '~~'
            if self.actual() == '~' and self.siguiente() == '~':
                texto += self.avanzar() + self.avanzar()
                self.agregar("COMENTARIO", texto)
                return

            texto += self.avanzar()

    """
    Lee una cadena de texto entre comillas dobles "...".
    Argumentos: Ninguno.
    Retorna: Nada.
    Errores: Registra error si la cadena no cierra antes del fin de línea o archivo.
    """
    def escanear_cadena(self):
        texto = self.avanzar()  # Consume la comilla inicial '"'

        while True:
            # Si se acaba la línea o el archivo sin encontrar la comilla de cierre
            if self.actual() is None or self.actual() == '\n':
                self.registrar_error(texto, mensaje="Cadena sin cerrar")
                return

            # Si encontramos la comilla de cierre '"'
            if self.actual() == '"':
                texto += self.avanzar()
                contenido_sin_comillas = texto[1:-1]
                self.agregar("CADENA", texto, contenido_sin_comillas)
                return

            texto += self.avanzar()

    """
    Lee números enteros o decimales (ej: 20 o 3.14)
    Argumentos: Ninguno.
    Retorna: Nada.
    Errores: Registra error si el decimal no tiene dígitos, o 3.1.1.1 o 3a
    """
    def escanear_numero(self):
        texto = ""
        while self.es_digito(self.actual()):
            texto += self.avanzar()

        es_decimal = False

        # Si encontramos un punto, revisamos si tiene dígitos a la derecha
        if self.actual() == '.':
            if self.es_digito(self.siguiente()):
                es_decimal = True
                texto += self.avanzar()  # Consume el '.'
                while self.es_digito(self.actual()):
                    texto += self.avanzar()
            else:
                # Punto sin dígitos después (ej: 3.)
                texto_invalido = texto + self.modo_panico()
                self.registrar_error(texto_invalido)
                return

        # Si viene más de un punto (ej: 1.5.0)
        if self.actual() == '.':
            texto_invalido = texto + self.modo_panico()
            self.registrar_error(texto_invalido)
            return

        # Si vienen letras o guión bajo pegados al número (ej: 1a)
        if self.es_letra(self.actual()) or self.actual() == '_':
            texto_invalido = texto + self.modo_panico()
            self.registrar_error(texto_invalido)
            return

        tipo = "DECIMAL" if es_decimal else "ENTERO"
        self.agregar(tipo, texto, texto)

    """
    Lee nombres de variables o palabras reservadas (ej: calavera, ritual, total).
    Argumentos: Ninguno.
    Retorna: Nada.
    Errores: Ninguno.
    """
    def escanear_identificador(self):
        texto = ""
        while self.actual() is not None and (self.es_letra(self.actual()) or self.es_digito(self.actual()) or self.actual() == '_'):
            texto += self.avanzar()

        # Caso especial para la palabra reservada compuesta "sin mana"
        if texto == "sin":
            resto = self.fuente[self.posicion:]
            resto_limpio = resto.lstrip(' \t')
            if resto_limpio.startswith("mana"):
                # Verificamos que sea la palabra completa y no algo como 'manantial'
                siguiente_char = resto_limpio[4:5]
                if not (self.es_letra(siguiente_char) or self.es_digito(siguiente_char) or siguiente_char == '_'):
                    espacios = len(resto) - len(resto_limpio)
                    for _ in range(espacios + 4):
                        self.avanzar()
                    texto = "sin mana"

        tipo = palabras_reservadas.get(texto, "IDENTIFICADOR")
        self.agregar(tipo, texto)

    """
    Bucle principal que recorre todo el código fuente y genera los tokens.
    Argumentos: Ninguno.
    Retorna: Lista con todos los tokens reconocidos.
    Errores: Activa modo pánico y registra errores al encontrar caracteres o secuencias inválidas.
    """
    def escanear(self):
        while self.actual() is not None:
            caracter = self.actual()

            # 1. Ignorar espacios en blanco y saltos de línea
            if caracter in [' ', '\t', '\r', '\n']:
                self.avanzar()
                continue

            # Marcar el inicio exacto del token
            self.marcar_inicio()

            # 2. Comentarios (inician con ~~)
            if caracter == '~' and self.siguiente() == '~':
                self.escanear_comentario()
                continue

            # 3. Cadenas de texto (inician con ")
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
            dos_caracteres = self.fuente[self.posicion:self.posicion + 2]
            if dos_caracteres in operadores_dobles:
                self.avanzar()
                self.avanzar()
                self.agregar(operadores_dobles[dos_caracteres], dos_caracteres)
                continue

            # 7. Símbolos individuales y operadores de un caracter (< , > , ☩ , ✦ , etc.)
            if caracter in simbolos:
                self.avanzar()
                self.agregar(simbolos[caracter], caracter)
                continue

            # 8. Caracter no reconocido: activar modo pánico y registrar error
            texto_invalido = self.modo_panico()
            self.registrar_error(texto_invalido)

        return self.tokens
