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

    #Consume y devuelve el token actual. Si no es el esperado regsitra un error y NO avanza:
    #se asume que el token esperado falta, asi el token encontrado lo puede usar la siguiente regla
    def consumir(self, tipo_esperado=None, contexto=""):
        tok = self.consultar()
        if tipo_esperado is not None and tok.tipo != tipo_esperado:

            #*****Esto es de la persona 5 para manejo de errores******
            self.errores.append(
                f"línea {tok.linea}, columna {tok.columna}: "
                f"se esperaba {tipo_esperado}, se encontró {tok.tipo} '{tok.contenido}'"
            )
            return tok  # no avanzar, el token encontrado no se pierde
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

    # -------------------------------------------------------------------------
    # Instrucciones
    # -------------------------------------------------------------------------

    # Tipos de token con los que puede iniciar una declaracion
    INICIO_DECLARACION = (
        "CALAVERA", "CANTICO", "ESENCIA", "LATIDO", "CENIZA", "FOSA"
    )

    # Analiza una instruccion y devuelve su nodo.
    # Regla gramatical:
    #   Instruccion ::= Comentario | Declaracion ☩ | Asignacion ☩
    #                 | Llamada ☩ | Sacrificio ☩ | Condicional | Bucle
    # Los comentarios se aceptan pero no generan nodo (se devuelve None).
    def parsear_instruccion(self):
        tok = self.consultar()

        # 1. Los comentarios se saltan, no aparecen en el arbol
        if tok.tipo == "COMENTARIO":
            self.consumir()
            return None

        # 2. Declaraciones: inician con un tipo (calavera, fosa, etc.)
        if self.coincide(*self.INICIO_DECLARACION):
            nodo = self.parsear_declaracion()
            self.exigir_fin_instruccion()
            return nodo

        # 3. Asignaciones: Nombre <- Expresion
        if tok.tipo == "IDENTIFICADOR" and \
                self.consultar(1).tipo == "ASIGNACION":
            nodo = self.parsear_asignacion()
            self.exigir_fin_instruccion()
            return nodo

        # 4. Condicionales: mana, sin mana, sin (no llevan ☩)
        if tok.tipo == "MANA":
            return self.parsear_condicional()

        # 5. Bucles: convocar y persistir (no llevan ☩)
        if tok.tipo == "CONVOCAR":
            return self.parsear_bucle_convocar()
        if tok.tipo == "PERSISTIR":
            return self.parsear_bucle_persistir()

        # 6. Ningun tipo de instruccion empieza con este token
        self.errores.append(
            f"línea {tok.linea}, columna {tok.columna}: "
            f"se esperaba una instrucción, se encontró "
            f"{tok.tipo} '{tok.contenido}'"
        )
        if tok.tipo != "EOF":
            self.consumir()
        return None

    # Exige el punto y coma de la muerte al final de una instruccion.
    # Regla gramatical: ... ☩
    # Si no esta se registra el error pero NO se consume el token, asi la
    # siguiente instruccion no se pierde.
    def exigir_fin_instruccion(self):
        if self.coincide("FIN_INSTRUCCION"):
            self.consumir()
            return

        tok = self.consultar()
        self.errores.append(
            f"línea {tok.linea}, columna {tok.columna}: "
            f"se esperaba '☩', se encontró {tok.tipo} '{tok.contenido}'"
        )

    # Analiza la declaracion de una variable o de una lista.
    # Regla gramatical:
    #   Declaracion ::= TipoPrimitivo Nombre <- Expresion
    #                 | "fosa" TipoLista Nombre <- ☾ ListaValores ☽
    def parsear_declaracion(self):

        # 1. Analiza el tipo
        tipo = self.parsear_tipo()

        # 2. Consume el nombre de la variable
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre de la variable")

        # 3. Crea el nodo Declaracion con la posicion del nombre
        nodo = NodoASA.desde_token("Declaracion", tok_nombre)
        nodo.agregar_hijo(tipo)

        # 4. Consume la flecha de asignacion
        self.consumir("ASIGNACION", "<-")

        # 5. Las fosas reciben una lista, los demas una expresion
        if tipo.contenido.startswith("fosa"):
            nodo.agregar_hijo(self.parsear_lista())
        else:
            nodo.agregar_hijo(self.parsear_expresion())
        return nodo

    # Analiza los valores de una lista.
    # Regla gramatical: Lista ::= ☾ (Expresion (, Expresion)*)? ☽
    def parsear_lista(self):

        # 1. Consume el corchete de apertura
        self.consumir("CORCHETE_IZQUIERDO", "☾")

        # 2. Crea el nodo Lista que agrupa los valores
        nodo = NodoASA("Lista", "", "")

        # 3. Si viene el corchete de cierre la lista esta vacia
        if not self.coincide("CORCHETE_DERECHO"):
            nodo.agregar_hijo(self.parsear_expresion())

            # 4. Los demas valores van separados por coma
            while self.coincide("COMA"):
                self.consumir("COMA")
                nodo.agregar_hijo(self.parsear_expresion())

        # 5. Consume el corchete de cierre
        self.consumir("CORCHETE_DERECHO", "☽")
        return nodo

    # Analiza la asignacion de un valor a una variable ya declarada.
    # Regla gramatical: Asignacion ::= Nombre <- Expresion
    def parsear_asignacion(self):

        # 1. Consume el nombre de la variable
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre de la variable")

        # 2. Crea el nodo Asignacion con la posicion del nombre
        nodo = NodoASA.desde_token("Asignacion", tok_nombre)

        # 3. Consume la flecha y analiza el valor asignado
        self.consumir("ASIGNACION", "<-")
        nodo.agregar_hijo(self.parsear_expresion())
        return nodo

    # Analiza un condicional completo con sus ramas opcionales.
    # Regla gramatical:
    #   Condicional ::= "mana" ⟅ ExpresionLogica ⟆ Bloque
    #                   BloqueSinMana BloqueSin
    #   BloqueSinMana ::= "sin mana" ⟅ ExpresionLogica ⟆ Bloque
    #                     BloqueSinMana | ε
    #   BloqueSin ::= "sin" Bloque | ε
    def parsear_condicional(self):

        # 1. Nodo que agrupa todas las ramas del condicional
        nodo = NodoASA("Condicional", "", "")

        # 2. Rama obligatoria: mana (if)
        nodo.agregar_hijo(self.parsear_rama_condicional("MANA", "Mana"))

        # 3. Cero o mas ramas sin mana (else if)
        while self.coincide("SIN_MANA"):
            nodo.agregar_hijo(
                self.parsear_rama_condicional("SIN_MANA", "SinMana")
            )

        # 4. Rama opcional sin (else), solo lleva bloque
        if self.coincide("SIN"):
            tok_sin = self.consumir("SIN")
            rama = NodoASA.desde_token("Sin", tok_sin, "")
            rama.agregar_hijo(self.parsear_bloque())
            nodo.agregar_hijo(rama)

        return nodo

    # Analiza una rama con condicion: mana o sin mana.
    # Regla gramatical: palabra ⟅ ExpresionLogica ⟆ Bloque
    def parsear_rama_condicional(self, tipo_token, tipo_nodo):

        # 1. Consume la palabra clave de la rama
        tok = self.consumir(tipo_token)

        # 2. Crea el nodo con la posicion de la palabra clave
        nodo = NodoASA.desde_token(tipo_nodo, tok, "")

        # 3. Condicion entre parentesis
        self.consumir("PARENTESIS_IZQUIERDO", "⟅")
        nodo.agregar_hijo(self.parsear_expresion())
        self.consumir("PARENTESIS_DERECHO", "⟆")

        # 4. Bloque que se ejecuta si se cumple la condicion
        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    # Analiza un bucle controlado (for).
    # Regla gramatical:
    #   BucleConvocar ::= "convocar" Tipo Nombre "en" Expresion Bloque
    def parsear_bucle_convocar(self):

        # 1. Consume la palabra clave del bucle
        self.consumir("CONVOCAR")

        # 2. Tipo y nombre de la variable que recorre el bucle
        tipo = self.parsear_tipo()
        tok_nombre = self.consumir("IDENTIFICADOR", "variable del bucle")

        # 3. Crea el nodo con el nombre y la posicion de la variable
        nodo = NodoASA.desde_token("BucleConvocar", tok_nombre)
        nodo.agregar_hijo(tipo)

        # 4. Expresion que se recorre despues de "en"
        self.consumir("EN", "en")
        nodo.agregar_hijo(self.parsear_expresion())

        # 5. Bloque que se repite
        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    # Analiza un bucle condicional (while).
    # Regla gramatical:
    #   BuclePersistir ::= "persistir" ⟅ ExpresionLogica ⟆ Bloque
    def parsear_bucle_persistir(self):

        # 1. Consume la palabra clave y crea el nodo con su posicion
        tok = self.consumir("PERSISTIR")
        nodo = NodoASA.desde_token("BuclePersistir", tok, "")

        # 2. Condicion entre parentesis
        self.consumir("PARENTESIS_IZQUIERDO", "⟅")
        nodo.agregar_hijo(self.parsear_expresion())
        self.consumir("PARENTESIS_DERECHO", "⟆")

        # 3. Bloque que se repite mientras se cumpla la condicion
        nodo.agregar_hijo(self.parsear_bloque())
        return nodo
