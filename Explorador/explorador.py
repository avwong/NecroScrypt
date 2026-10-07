
#Caracteres usados para hacer la recuperacion en modo panico
#Creo que estos son todos???????

caracteres_seguros = {'☩', '⟆', '✧', '☽', '⟅', '✦', '☾', '\n'}

#-----------------------------------------------------------------------------------------------------------------------------------------

#Clase Token que representa cada uno de los token encontrados por el explorador
class Token:
    
    def __init__(self, tipo, lexema, linea, columna, atributo = ""):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.atributo = atributo
        
    def __repr__(self):
        return f'<"{self.tipo}", "{self.lexema}", "{self.atributo}">'
    

#-----------------------------------------------------------------------------------------------------------------------------------------

#Clase ErroLexico, Define como se ve la infromaicon que se va a mostrar en pantalla cuando encuentre un error
class ErrorLexico:
    
    def __init__(self, mensaje, linea, columna, caracter, lexema_invalido, contexto, marca):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        self.caracter = caracter
        self.lexema_invalido = lexema_invalido
        self.contexto = contexto
        self.marca = marca                  #La marca es el techito ^
        
    def __str__(self):
        partes = [
            f"Error lexico: {self.mensaje}",
            f"Ubicacion: Linea {self.linea}, Columna {self.columna}",
        ]
        
        if self.caracter is not None: 
            partes.append(f"Caracter: '{self.caracter}'")
            
        if self.lexema_invalido:
            partes.append(f"Lexema invalido: '{self.lexema_invalido}'")
        if self.contexto is not None:
            partes.append("Contexto:")
            partes.append(self.contexto)
            partes.append(self.marca)
        
        return "\n".join(partes)
    
    
# Los errores los imprime parecido a esto:

# Error léxico: carácter '@' no pertenece al alfabeto del lenguaje
# Ubicación: línea 3, columna 1
# Carácter: '@' 
# Lexema: '@'
# Contexto:
#   @@@ basura @@@
#   ^

#-----------------------------------------------------------------------------------------------------------------------------------------


# Clase Explorador que se encarga de recorrer el texto y generar los tokens
# El manejo de errores se hace por medio de modo panico 
class Explorador:
    
    def __init__(self, fuente):
        self.fuente = fuente
        self.linea = 1
        self.columna = 1
        self.posicion = 0
        self.tokens = []
        self.errores = []
        self.lineas = fuente.splitlines()
        # Posicion donde empieza el token que se esta leyendo (se actualiza con marcar_inicio)
        self.inicio_linea = 1
        self.inicio_columna = 1
        
    #----------------------------------------------------------
    #Funciones Auxiliares:
    
    # Segun la gramatica: Letra ::= [a-z] | [A-Z]  (sin tildes ni ñ en los nombres)
    @staticmethod
    def es_letra(caracter):
        return caracter is not None and (('a' <= caracter <= 'z') or ('A' <= caracter <= 'Z'))
    
    # Numero ::= [0-9]+
    @staticmethod
    def es_digito(caracter):
        return caracter is not None and '0' <= caracter <= '9'
        
    
    def actual(self):
        if self.posicion < len(self.fuente):
            return self.fuente[self.posicion]
        else:
            return None
        
    def siguiente(self, offset = 1):
        indice = self.posicion + offset
        if indice < len(self.fuente):
            return self.fuente[indice]
        else:
            return None
    
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
    
    # Guarda la posicion actual como el inicio del token que se va a leer
    # Se debe llamar en escanear() ANTES de empezar a consumir cada token
    def marcar_inicio(self):
        self.inicio_linea = self.linea
        self.inicio_columna = self.columna
    
    # Agrega un token. Si no se pasa linea/columna, usa la posicion guardada por marcar_inicio()
    # (es decir, donde EMPIEZA el token, no donde termina)
    def agregar(self, tipo, lexema, atributo = "", linea = None, columna = None):
        if linea is None:
            linea = self.inicio_linea
        if columna is None:
            columna = self.inicio_columna
        
        partes = []
        
        if atributo:
            partes.append(atributo)
        partes.append(f"línea = {linea}")
        partes.append(f"columna = {columna}")
        
        atributo_final = ", ".join(partes)
        
        self.tokens.append(Token(tipo, lexema, linea, columna, atributo_final))
    
    # Funcion para agregar un error lexico a la lista de errores
    # Arma el contexto (la linea de codigo original) y la marca ^ debajo de la columna del error
    def registrar_error(self, mensaje, linea, columna, caracter = None, lexema_invalido = ""):
        if 1 <= linea <= len(self.lineas):
            contexto = self.lineas[linea - 1]
            # Se respetan los tabs para que el ^ quede alineado con el caracter
            marca = "".join('\t' if c == '\t' else ' ' for c in contexto[:columna - 1]) + "^"
        else:
            contexto = None
            marca = ""
        
        self.errores.append(ErrorLexico(mensaje, linea, columna, caracter, lexema_invalido, contexto, marca))
    
    # Funcion para avanzar en modo panico
    # Descarta caracteres hasta encontrar uno de los caracteres_seguros (o el fin del archivo)
    # NO consume el caracter seguro, para que despues se tokenice normalmente
    # Retorna el texto descartado, que se usa como lexema invalido en el error
    def modo_panico(self):
        descartado = ""
        
        # Siempre se consume al menos el caracter malo, para no quedarse en un ciclo infinito
        if self.actual() is not None:
            descartado += self.avanzar()
        
        while self.actual() is not None and self.actual() not in caracteres_seguros:
            descartado += self.avanzar()
        
        return descartado
    
    # Funcion principal del explorador.
    # Recorre la fuente y decide que funcion debe procesar
    # cada componente lexico.
    def escanear(self):

        simbolos = {
            '☩': "FIN_INSTRUCCION",
            '⟅': "PARENTESIS_IZQUIERDO",
            '⟆': "PARENTESIS_DERECHO",
            '✦': "INICIO_BLOQUE",
            '✧': "FIN_BLOQUE",
            '☽': "CORCHETE_IZQUIERDO",
            '☾': "CORCHETE_DERECHO"
        }

        while self.actual() is not None:

            caracter = self.actual()

            # Espacios y tabulaciones no generan tokens
            if caracter in {' ', '\t', '\r'}:
                self.avanzar()
                continue

            # Saltos de linea
            if caracter == '\n':
                self.avanzar()
                continue

            # Se guarda donde comienza el componente lexico
            self.marcar_inicio()

            # Comentarios: ~~ comentario ~~
            if caracter == '~' and self.siguiente() == '~':
                self.escanear_comentario()
                continue

            # Cadenas
            if caracter == '"':
                self.escanear_cadena()
                continue

            # Numeros enteros o decimales
            if self.es_digito(caracter):
                self.escanear_numero()
                continue

            # Identificadores y palabras reservadas
            if self.es_letra(caracter):
                self.escanear_identificador()
                continue

            # Operador de asignacion <-
            if caracter == '<' and self.siguiente() == '-':
                self.avanzar()
                self.avanzar()
                self.agregar("ASIGNACION", "<-")
                continue

            # Simbolos simples del lenguaje
            if caracter in simbolos:
                tipo = simbolos[caracter]
                self.avanzar()
                self.agregar(tipo, caracter)
                continue

            # Si no entro en ningun caso, es un error lexico
            linea_error = self.linea
            columna_error = self.columna
            caracter_error = caracter

            lexema_invalido = self.modo_panico()

            self.registrar_error(
                "Caracter o secuencia no reconocida por el lenguaje",
                linea_error,
                columna_error,
                caracter_error,
                lexema_invalido
            )

        return self.tokens
        
# Funcion para escanear comentarios
# Funcion para escanear cadenas
# Funcion para escanear numeros (Enteros y decimales)
# Funcion para escanear identificadores