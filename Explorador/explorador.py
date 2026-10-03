
#Caracteres usados para hacer la recuperacion en modo panico
#Creo que estos son todos???????

caracteres_seguros = {'☩', '⟆', '✧', '☽', '⟅', '✦', '☾', '\n'}

#-----------------------------------------------------------------------------------------------------------------------------------------

#Clase Token que representa cada uno de los token encontrados por el explorador
class Token:
    
    def __intit__(self, tipo, lexema, linea, columna, atriuto = ""):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.atributo = atriuto
        
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
    
    print("Explorador")
        
        