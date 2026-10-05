
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
        
    #----------------------------------------------------------
    #Funciones Auxiliares:
    
    def es_letra(caracter):
        if caracter is not None and caracter.isalpha():
            return True
        
    def es_digito(caracter):
        if caracter is not None and 0 <= caracter <= '9':
            return True
        
    
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
    
    def agregar(self, tipo, lexema, atributo = "", linea = None, columna = None):
        if linea is None:
            linea = self.linea
        if columna is None:
            columna = self.columna
        
        partes = []
        
        if atributo:
            partes.append(atributo)
        partes.append(f"línea = {linea}")
        partes.append(f"columna = {columna}")
        
        atributo_final = ", ".join(partes)
        
        self.tokens.append(Token(tipo, lexema, linea, columna, atributo_final))
    
    #Hacer funcion de escanear: (Esta la que hace todo)
        #Se hace un while que vaya caracter por caracter y vaya haciendo llamdas a cada funcion de escaneo
        # para los de comparacion se revisa el siguiente caracter
        # se revisa simbolos, las estrellas y esos
    
    
    
    # Funcion para escanear comentarios
    # Funcion para escanear cadenas
    # Funcion para escanear numeros (Enteros y decimales)
    # Funcion para escanear identificadores
        
        