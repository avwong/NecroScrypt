""" la clase del analizador

El objetivo es que retorne un ASA Arbol Syntax Abstracta
Ya listo para el verificador

DISEÑO DEL ASA:

Formato de impresion (un nodo por linea):
    <"Tipo", "Contenido", "Atributos">

Convenciones:
    - Atributos: "línea = L, columna = C", tomado del token que origino el
      nodo (igual que el explorador). Los nodos agrupadores sin token usan ""
    - No aparecen en el arbol: ☩ ✦ ✧ ⟅ ⟆ ☾ ☽ <- , ⚯ ni las palabras clave que
      ya definen el tipo de nodo
    - Los comentarios ~~...~~ se omiten del arbol (el parser los acepta y los
      salta)
    - TipoRetorno solo existe si el ritual tiene ⚯; si no, no hay nodo.
    - Tipo es un nodo hijo (hoja), nunca un atributo del padre.
    - Los operadores van en el contenido del nodo binario. La precedencia
      queda resuelta por la forma del arbol:
      2 ensamblar 3 infestar 4 -> ensamblar(2, infestar(3, 4)) = 14

    Tipo de nodo         Contenido                        Hijos
    -------------------  -------------------------------  ------------------
    Programa             ""                               Ritual o
                                                          instrucciones
    Ritual               nombre                           Parametros,
                                                          TipoRetorno (si
                                                          existe), Bloque
    Parametros           ""                               Parametro*
    Parametro            nombre                           Tipo
    TipoRetorno          ""                               Tipo
    Tipo                 calavera, fosa calavera, etc.    ninguno (hoja)
    Bloque               ""                               instrucciones*
    Declaracion          nombre                           Tipo, valor
                                                          (expresion o Lista)
    Lista                ""                               expresiones*
    Asignacion           nombre                           expresion
    Sacrificio           ""                               expresion
    Condicional          ""                               Mana, SinMana*,
                                                          Sin?
    Mana                 ""                               condicion, Bloque
    SinMana              ""                               condicion, Bloque
    Sin                  ""                               Bloque
    BucleConvocar        nombre de la variable            Tipo, expresion
                                                          iterada, Bloque
    BuclePersistir       ""                               condicion, Bloque
    LlamadaRitual        nombre                           Argumentos
    Argumentos           ""                               expresion o Tipo*
    OperacionLogica      y / o                            izquierda, derecha
    Comparacion          ==, !=, <, >, <=, >=             izquierda, derecha
    OperacionAritmetica  ensamblar, mutilar, infestar,    izquierda, derecha
                         desmembrar, restos
    Identificador        nombre                           ninguno
    Entero / Decimal     el numero                        ninguno
    Cadena               texto sin comillas               ninguno
    Booleano             vivo / muerto                    ninguno
    Ceniza               ceniza                           ninguno

"""

from Analizador.nodo_asa import NodoASA
from Explorador.asa import Token


class Analizador:
  
  
    def __init__(self, tokens):
      
        self.tokens = list(tokens)
        
        #Esto de aqui es para poder marcar el EOF, ya que el explorador no lo manda en la lista
        if not self.tokens or self.tokens[-1].tipo != "EOF":
            ultimo = self.tokens[-1] if self.tokens else None
            linea = ultimo.linea if ultimo else 1
            columna = ultimo.columna if ultimo else 1
            self.tokens.append(Token("EOF", "", linea, columna))
            
        self.pos = 0
        self.errores = []  # P5: formato y recuperación


#-------------------------------------------------------------------------------------------------------------------------------
    #Metodos Auxiliares
    
    #Consulta uno de los tokens sin consumirlo. Si se conuslta fuera del rango de la lista se devueleve EOF
    def consultar(self, offset=0):
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]


    #Revisa si el token actual pertenece a alguno de los tipos recibidos como argumento
    def coincide(self, *tipos):
        return self.consultar().tipo in tipos

    #Consume y devuelve el token actual. Si no es el esperado regsitra un error. Si es EOF no avanza
    def consumir(self, tipo_esperado=None, contexto=""):
        tok = self.consultar()
        if tipo_esperado is not None and tok.tipo != tipo_esperado:
            
            #*****Esto es de la persona 5 para manejo de errores******
            self.errores.append(
                f"línea {tok.linea}, columna {tok.columna}: "
                f"se esperaba {tipo_esperado}, se encontró {tok.tipo} '{tok.contenido}'"
            )
            if tok.tipo == "EOF":
                return tok  # no avanzar sobre EOF
        self.pos += 1
        return tok

#------------------------------------------------------------------------------------------------------------------------------------
    
    #Estructura Macro

    #Analiza el programa completo y devuelve su nodo raiz. Crea un nodo Programa y despues analiza cad alemento hasta encontrar el EOF
    def analizar(self):
        programa = NodoASA("Programa", "", "")
        while not self.coincide("EOF"):
            elemento = self.parsear_elemento()
            if elemento is not None:
                programa.agregar_hijo(elemento)
        return programa


    # Analiza un elemento de nivel superior. 
    #Regla gramtaical: Elemento ::= Ritual | Instruccion
    def parsear_elemento(self):
        if self.coincide("RITUAL"):
            return self.parsear_ritual()
        return self.parsear_instruccion()  # Esta parte le toca a la persona 3*******************


    #Analiza la declaracion de un ritual
    #Regla gramatical: Ritual ::= RITUAL Nombre ⟅ Parametros ⟆ TipoRetorno Bloque
    def parsear_ritual(self):
      
        # 1. Consumir palabra clave que inica el ritual
        self.consumir("RITUAL", "inicio de ritual")
        
        # 2. Identificador que representa su nombre
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre del ritual")
        
        # 3. Crea el Nodo Ritual
        ritual = NodoASA("Ritual", tok_nombre.contenido,
                         f"línea = {tok_nombre.linea}, columna = {tok_nombre.columna}")
        
        # 4. Consume apertura de parentesis
        self.consumir("PARENTESIS_IZQUIERDO", "⟅")
        
        # 5. Analiza los paramteros y los agrega como nodos hijos
        ritual.agregar_hijo(self.parsear_parametros())
        
        # 6. Consume cierre de parentesis
        self.consumir("PARENTESIS_DERECHO", "⟆")
        
        # 7. analiza el tipo de retorno
        tipo_ret = self.parsear_tipo_retorno()
        if tipo_ret is not None:
            ritual.agregar_hijo(tipo_ret)
            
        # 8. Analiza y agrega el bloque de instricciones del ritual
        ritual.agregar_hijo(self.parsear_bloque())
        return ritual


    #Analiza la lista de parametros de un ritual
    # Regla Gramtical: Parametros ::= Parametro (',' Parametro)* | ε
    def parsear_parametros(self):

        # 1. Nodo que contiene todos los paramteros
        nodo = NodoASA("Parametros", "", "")
        
        # 2. Si aparece el parentesis de cierre es que no hay parametros
        if self.coincide("PARENTESIS_DERECHO"):
            return nodo
          
        # 3. Analizar el primer parametro
        nodo.agregar_hijo(self.parsear_parametro())
        
        # 4. Analiza los paramteros separados por coma
        while self.coincide("COMA"):
            self.consumir("COMA")
            nodo.agregar_hijo(self.parsear_parametro())
        return nodo


    # Analiza la declaracion de un parametro
    # Regla Gramatical: Parametro ::= Tipo Nombre
    def parsear_parametro(self):
      
        # 1. Analiza el tipo
        tipo = self.parsear_tipo()
        
        # 2. Consume el identificador que es el nombre del parametro
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre del parámetro")
        
        # 3. Crea el nodo paramtero con su nombre y posicion
        nodo = NodoASA("Parametro", tok_nombre.contenido,
                       f"línea = {tok_nombre.linea}, columna = {tok_nombre.columna}")
        
        # 4. El tipo se representa como un nodo hijo
        nodo.agregar_hijo(tipo)
        return nodo


    #Analiza el tipo de retorno opcional de un ritual
    #Regla gramatical: TipoRetorno ::= ⚯ Tipo | ε  (no crear nodo si no hay ⚯)
    def parsear_tipo_retorno(self):

        # 1. Sin el simbolo no se declra un tipo de retorno
        if not self.coincide("ASIGNACION_RETORNO"):
            return None
        # 2. Consume el simbolo que declara el tipo de retorno
        self.consumir("ASIGNACION_RETORNO")
        
        # 3. Crea el nodo tipoRetorno
        nodo = NodoASA("TipoRetorno", "", "")
        
        # 4. Analiza el tipo y lo agrega como hijo
        nodo.agregar_hijo(self.parsear_tipo())
        return nodo


    # Ananliza un tipo primitivo o un tipo de arreglo
    # Regla Gramatical: Tipo ::= TipoPrimitivo | TipoArreglo
    def parsear_tipo(self):
        
        # 1. Revisa si empieza con Fosa que es un arreglo
        if self.coincide("FOSA"):
            # 1.1 Consume el token inicial del tipo de arreglo
            tok = self.consumir("FOSA")
            contenido = "fosa"
            
            # 1.2 Comprueba que aparezca un tipo permitido para los elemetos
            if self.coincide("CALAVERA", "CANTICO", "ESENCIA", "LATIDO"):
                sub = self.consumir()
                contenido = f"fosa {sub.contenido}"
            else:
                # *************** ESTO ES DE LA PERSONA 5 *********************
                self.errores.append(
                    f"línea = {tok.linea}, columna = {tok.columna}: "
                    f"se esperaba calavera/cantico/esencia/latido tras 'fosa'"
                )
                
            # 1.3 Devuelve el nodo Tipo con la posicion del token FOSA
            return NodoASA("Tipo", contenido,
                           f"línea = {tok.linea}, columna = {tok.columna}")

        
        # 2. Revisa si el token actual es un tipo primitivo
        if self.coincide("CALAVERA", "CANTICO", "ESENCIA", "LATIDO", "CENIZA"):
          
            # 2.1 Consume el token del tipo
            tok = self.consumir()
            return NodoASA("Tipo", tok.contenido,
                           f"línea = {tok.linea}, columna = {tok.columna}")

        # 3 **************** ESTO ES DE LA PERSONA 5 EN CASO DE QUE NO SE ENCUETRE NINGUN TIPO VALIDO *********** 
        tok = self.consultar()
        self.errores.append(
            f"línea = {tok.linea}, columna = {tok.columna}: se esperaba un tipo"
        )
        return NodoASA("Tipo", "", f"línea = {tok.linea}, columna = {tok.columna}")


    #Analiza un bloque de instrucciones
    # Regla Gramatical: Bloque ::= ✦ Instrucciones ✧
    def parsear_bloque(self):
        
        # 1. Consume el simbolo que hace la paertura del bloque
        self.consumir("INICIO_BLOQUE", "inicio de bloque ✦")
        
        # 2. Crea el nodo Bloque
        nodo = NodoASA("Bloque", "", "")
        
        #3. Continua hasta que no se eneuntre el simbolo de cierre del bloque
        while not self.coincide("FIN_BLOQUE", "EOF"):
            # *********** ESTO ES DE LA PERSONA 5 PARA HACER EL MODO PANICO
            
            # 4. Analiza la siguiente instruccion
            instr = self.parsear_instruccion()
            
            # 5. Si se obtiene in nodo valido se agrega al bloque
            if instr is not None:
                nodo.agregar_hijo(instr)
        # 6. Consume el simbolo que cierra el bloque
        self.consumir("FIN_BLOQUE", "cierre de bloque ✧")
        return nodo

    # -------------------------------------------------------------------------
    # Persona 4 - Expresiones
    # -------------------------------------------------------------------------

    """
    Analiza una expresion completa respetando la precedencia de operadores.
    La precedencia, de menor a mayor, es:
    o -> y -> comparaciones -> suma/resta -> multiplicacion/division/restos.
    """
    def parsear_expresion(self):
        return self.parsear_logica_o()


    # Analiza el operador logico "o".
    def parsear_logica_o(self):
        nodo = self.parsear_logica_y()

        while self.coincide("O"):
            operador = self.consumir()
            derecha = self.parsear_logica_y()
            nodo = self.crear_operacion_binaria(
                "OperacionLogica", operador, nodo, derecha
            )

        return nodo


    # Analiza el operador logico "y".
    def parsear_logica_y(self):
        nodo = self.parsear_comparacion()

        while self.coincide("Y"):
            operador = self.consumir()
            derecha = self.parsear_comparacion()
            nodo = self.crear_operacion_binaria(
                "OperacionLogica", operador, nodo, derecha
            )

        return nodo


    # Analiza comparaciones: ==, !=, <, >, <= y >=.
    def parsear_comparacion(self):
        nodo = self.parsear_suma_resta()

        if self.coincide(
            "IGUAL_QUE",
            "DIFERENTE_QUE",
            "MENOR_QUE",
            "MAYOR_QUE",
            "MENOR_IGUAL",
            "MAYOR_IGUAL"
        ):
            operador = self.consumir()
            derecha = self.parsear_suma_resta()
            nodo = self.crear_operacion_binaria(
                "Comparacion", operador, nodo, derecha
            )

        return nodo


    # Analiza ensamblar (+) y mutilar (-).
    def parsear_suma_resta(self):
        nodo = self.parsear_producto()

        while self.coincide("ENSAMBLAR", "MUTILAR"):
            operador = self.consumir()
            derecha = self.parsear_producto()
            nodo = self.crear_operacion_binaria(
                "OperacionAritmetica", operador, nodo, derecha
            )

        return nodo


    # Analiza infestar (*), desmembrar (/) y restos (%).
    # Estos operadores tienen mayor precedencia que ensamblar y mutilar.
    def parsear_producto(self):
        nodo = self.parsear_primaria()

        while self.coincide("INFESTAR", "DESMEMBRAR", "RESTOS"):
            operador = self.consumir()
            derecha = self.parsear_primaria()
            nodo = self.crear_operacion_binaria(
                "OperacionAritmetica", operador, nodo, derecha
            )

        return nodo


    # Analiza los valores basicos que pueden formar una expresion.
    def parsear_primaria(self):
        token = self.consultar()

        tipos_simples = {
            "ENTERO": "Entero",
            "DECIMAL": "Decimal",
            "IDENTIFICADOR": "Identificador",
            "VIVO": "Booleano",
            "MUERTO": "Booleano",
            "CENIZA": "Ceniza"
        }

        if token.tipo in tipos_simples:
            self.consumir()
            return NodoASA.desde_token(
                tipos_simples[token.tipo],
                token
            )

        if token.tipo == "CADENA":
            self.consumir()
            contenido = token.contenido[1:-1]
            return NodoASA.desde_token(
                "Cadena",
                token,
                contenido
            )

        # Permite agrupar expresiones entre parentesis.
        if token.tipo == "PARENTESIS_IZQUIERDO":
            self.consumir()
            nodo = self.parsear_expresion()
            self.consumir(
                "PARENTESIS_DERECHO",
                "cierre de expresion"
            )
            return nodo

        # Persona 5 podra complementar la recuperacion del error.
        self.errores.append(
            f"línea {token.linea}, columna {token.columna}: "
            f"se esperaba una expresión, se encontró "
            f"{token.tipo} '{token.contenido}'"
        )

        if token.tipo != "EOF":
            self.consumir()

        return None


    # Crea un nodo de operacion con sus dos operandos como hijos.
    def crear_operacion_binaria(
        self, tipo, operador, izquierda, derecha
    ):
        nodo = NodoASA(
            tipo,
            operador.contenido,
            f"línea = {operador.linea}, columna = {operador.columna}"
        )

        nodo.agregar_hijo(izquierda)
        nodo.agregar_hijo(derecha)

        return nodo







#Esto es de la persona 3, lo pongo pq mas arriba lo uso
def parsear_instruccion(self):
    self.consumir()
    return None