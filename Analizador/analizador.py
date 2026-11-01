"""
Analizador sintáctico de NecroScrypt.

Recibe la lista de tokens del explorador y construye el Árbol de Sintaxis
Abstracta (ASA) que se le pasa al verificador.

Formato de impresión (un nodo por línea):
    <"Tipo", "Contenido", "Atributos">

Convenciones:
    - Atributos: "línea = L, columna = C", tomado del token que originó el
      nodo (igual que el explorador). Los nodos agrupadores sin token usan "".
    - No aparecen en el árbol: ☩ ✦ ✧ ⟅ ⟆ ☾ ☽ <- , ⚯ ni las palabras clave que
      ya definen el tipo de nodo.
    - Los comentarios ~~...~~ se aceptan pero se omiten del árbol.
    - TipoRetorno solo existe si el ritual tiene ⚯.
    - Tipo es un nodo hijo (hoja), nunca un atributo del padre.
    - Los operadores van en el contenido del nodo binario. La precedencia
      queda resuelta por la forma del árbol:
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

        # El explorador no agrega EOF, así que se agrega aquí
        if not self.tokens or self.tokens[-1].tipo != "EOF":
            ultimo = self.tokens[-1] if self.tokens else None
            linea = ultimo.linea if ultimo else 1
            columna = ultimo.columna if ultimo else 1
            self.tokens.append(Token("EOF", "", linea, columna))

        self.pos = 0
        self.errores = []

    # -------------------------------------------------------------------------
    # Métodos auxiliares
    # -------------------------------------------------------------------------

    # Devuelve un token sin consumirlo. Fuera de rango devuelve EOF.
    def consultar(self, offset=0):
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    # Revisa si el token actual es de alguno de los tipos recibidos.
    def coincide(self, *tipos):
        return self.consultar().tipo in tipos

    # Consume y devuelve el token actual. Si no es el esperado registra un
    # error y no avanza: se asume que el token esperado falta, así el token
    # encontrado lo puede usar la siguiente regla.
    def consumir(self, tipo_esperado=None, contexto=""):
        tok = self.consultar()
        if tipo_esperado is not None and tok.tipo != tipo_esperado:
            self.errores.append(
                f"línea {tok.linea}, columna {tok.columna}: "
                f"se esperaba {tipo_esperado}, se encontró {tok.tipo} '{tok.contenido}'"
            )
            return tok
        self.pos += 1
        return tok

    # -------------------------------------------------------------------------
    # Estructura del programa
    # -------------------------------------------------------------------------

    # Analiza el programa completo y devuelve el nodo raíz.
    def analizar(self):
        programa = NodoASA("Programa", "", "")
        while not self.coincide("EOF"):
            elemento = self.parsear_elemento()
            if elemento is not None:
                programa.agregar_hijo(elemento)
        return programa

    # Elemento ::= Ritual | Instruccion
    def parsear_elemento(self):
        if self.coincide("RITUAL"):
            return self.parsear_ritual()
        return self.parsear_instruccion()

    # Ritual ::= RITUAL Nombre ⟅ Parametros ⟆ TipoRetorno Bloque
    def parsear_ritual(self):
        self.consumir("RITUAL", "inicio de ritual")
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre del ritual")

        ritual = NodoASA("Ritual", tok_nombre.contenido,
                         f"línea = {tok_nombre.linea}, columna = {tok_nombre.columna}")

        self.consumir("PARENTESIS_IZQUIERDO", "⟅")
        ritual.agregar_hijo(self.parsear_parametros())
        self.consumir("PARENTESIS_DERECHO", "⟆")

        tipo_ret = self.parsear_tipo_retorno()
        if tipo_ret is not None:
            ritual.agregar_hijo(tipo_ret)

        ritual.agregar_hijo(self.parsear_bloque())
        return ritual

    # Parametros ::= Parametro (',' Parametro)* | ε
    def parsear_parametros(self):
        nodo = NodoASA("Parametros", "", "")

        if self.coincide("PARENTESIS_DERECHO"):
            return nodo

        nodo.agregar_hijo(self.parsear_parametro())
        while self.coincide("COMA"):
            self.consumir("COMA")
            nodo.agregar_hijo(self.parsear_parametro())
        return nodo

    # Parametro ::= Tipo Nombre
    def parsear_parametro(self):
        tipo = self.parsear_tipo()
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre del parámetro")

        nodo = NodoASA("Parametro", tok_nombre.contenido,
                       f"línea = {tok_nombre.linea}, columna = {tok_nombre.columna}")
        nodo.agregar_hijo(tipo)
        return nodo

    # TipoRetorno ::= ⚯ Tipo | ε  (sin ⚯ no se crea nodo)
    def parsear_tipo_retorno(self):
        if not self.coincide("ASIGNACION_RETORNO"):
            return None
        self.consumir("ASIGNACION_RETORNO")

        nodo = NodoASA("TipoRetorno", "", "")
        nodo.agregar_hijo(self.parsear_tipo())
        return nodo

    # Tipo ::= TipoPrimitivo | TipoArreglo
    def parsear_tipo(self):
        # Arreglo: fosa seguido del tipo de sus elementos
        if self.coincide("FOSA"):
            tok = self.consumir("FOSA")
            contenido = "fosa"

            if self.coincide("CALAVERA", "CANTICO", "ESENCIA", "LATIDO"):
                sub = self.consumir()
                contenido = f"fosa {sub.contenido}"
            else:
                self.errores.append(
                    f"línea = {tok.linea}, columna = {tok.columna}: "
                    f"se esperaba calavera/cantico/esencia/latido tras 'fosa'"
                )

            return NodoASA("Tipo", contenido,
                           f"línea = {tok.linea}, columna = {tok.columna}")

        if self.coincide("CALAVERA", "CANTICO", "ESENCIA", "LATIDO", "CENIZA"):
            tok = self.consumir()
            return NodoASA("Tipo", tok.contenido,
                           f"línea = {tok.linea}, columna = {tok.columna}")

        tok = self.consultar()
        self.errores.append(
            f"línea = {tok.linea}, columna = {tok.columna}: se esperaba un tipo"
        )
        return NodoASA("Tipo", "", f"línea = {tok.linea}, columna = {tok.columna}")

    # Bloque ::= ✦ Instrucciones ✧
    def parsear_bloque(self):
        self.consumir("INICIO_BLOQUE", "inicio de bloque ✦")
        nodo = NodoASA("Bloque", "", "")

        while not self.coincide("FIN_BLOQUE", "EOF"):
            instr = self.parsear_instruccion()
            if instr is not None:
                nodo.agregar_hijo(instr)

        self.consumir("FIN_BLOQUE", "cierre de bloque ✧")
        return nodo

    # -------------------------------------------------------------------------
    # Expresiones
    # -------------------------------------------------------------------------

    # Analiza una expresión completa respetando la precedencia, de menor a
    # mayor: o -> y -> comparaciones -> suma/resta -> multiplicación/división/restos.
    def parsear_expresion(self):
        return self.parsear_logica_o()

    # Operador lógico "o".
    def parsear_logica_o(self):
        nodo = self.parsear_logica_y()

        while self.coincide("O"):
            operador = self.consumir()
            derecha = self.parsear_logica_y()
            nodo = self.crear_operacion_binaria(
                "OperacionLogica", operador, nodo, derecha
            )

        return nodo

    # Operador lógico "y".
    def parsear_logica_y(self):
        nodo = self.parsear_comparacion()

        while self.coincide("Y"):
            operador = self.consumir()
            derecha = self.parsear_comparacion()
            nodo = self.crear_operacion_binaria(
                "OperacionLogica", operador, nodo, derecha
            )

        return nodo

    # Comparaciones: ==, !=, <, >, <= y >=.
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

    # ensamblar (+) y mutilar (-).
    def parsear_suma_resta(self):
        nodo = self.parsear_producto()

        while self.coincide("ENSAMBLAR", "MUTILAR"):
            operador = self.consumir()
            derecha = self.parsear_producto()
            nodo = self.crear_operacion_binaria(
                "OperacionAritmetica", operador, nodo, derecha
            )

        return nodo

    # infestar (*), desmembrar (/) y restos (%).
    def parsear_producto(self):
        nodo = self.parsear_primaria()

        while self.coincide("INFESTAR", "DESMEMBRAR", "RESTOS"):
            operador = self.consumir()
            derecha = self.parsear_primaria()
            nodo = self.crear_operacion_binaria(
                "OperacionAritmetica", operador, nodo, derecha
            )

        return nodo

    # Valores básicos de una expresión: literales, identificadores y
    # expresiones entre paréntesis.
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

        if token.tipo == "PARENTESIS_IZQUIERDO":
            self.consumir()
            nodo = self.parsear_expresion()
            self.consumir(
                "PARENTESIS_DERECHO",
                "cierre de expresion"
            )
            return nodo

        self.errores.append(
            f"línea {token.linea}, columna {token.columna}: "
            f"se esperaba una expresión, se encontró "
            f"{token.tipo} '{token.contenido}'"
        )

        if token.tipo != "EOF":
            self.consumir()

        return None

    # Crea un nodo de operación con sus dos operandos como hijos.
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

    # Tipos de token con los que puede iniciar una declaración
    INICIO_DECLARACION = (
        "CALAVERA", "CANTICO", "ESENCIA", "LATIDO", "CENIZA", "FOSA"
    )

    # Instruccion ::= Comentario | Declaracion ☩ | Asignacion ☩
    #               | Llamada ☩ | Sacrificio ☩ | Condicional | Bucle
    # Los comentarios se aceptan pero no generan nodo (se devuelve None).
    def parsear_instruccion(self):
        tok = self.consultar()

        if tok.tipo == "COMENTARIO":
            self.consumir()
            return None

        if self.coincide(*self.INICIO_DECLARACION):
            nodo = self.parsear_declaracion()
            self.exigir_fin_instruccion()
            return nodo

        if tok.tipo == "IDENTIFICADOR" and \
                self.consultar(1).tipo == "ASIGNACION":
            nodo = self.parsear_asignacion()
            self.exigir_fin_instruccion()
            return nodo

        # Condicionales y bucles no llevan ☩
        if tok.tipo == "MANA":
            return self.parsear_condicional()

        if tok.tipo == "CONVOCAR":
            return self.parsear_bucle_convocar()
        if tok.tipo == "PERSISTIR":
            return self.parsear_bucle_persistir()

        self.errores.append(
            f"línea {tok.linea}, columna {tok.columna}: "
            f"se esperaba una instrucción, se encontró "
            f"{tok.tipo} '{tok.contenido}'"
        )
        if tok.tipo != "EOF":
            self.consumir()
        return None

    # Exige ☩ al final de una instrucción. Si falta se registra el error pero
    # no se consume el token, así la siguiente instrucción no se pierde.
    def exigir_fin_instruccion(self):
        if self.coincide("FIN_INSTRUCCION"):
            self.consumir()
            return

        tok = self.consultar()
        self.errores.append(
            f"línea {tok.linea}, columna {tok.columna}: "
            f"se esperaba '☩', se encontró {tok.tipo} '{tok.contenido}'"
        )

    # Declaracion ::= TipoPrimitivo Nombre <- Expresion
    #               | "fosa" TipoLista Nombre <- ☾ ListaValores ☽
    def parsear_declaracion(self):
        tipo = self.parsear_tipo()
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre de la variable")

        nodo = NodoASA.desde_token("Declaracion", tok_nombre)
        nodo.agregar_hijo(tipo)

        self.consumir("ASIGNACION", "<-")

        # Las fosas reciben una lista, los demás tipos una expresión
        if tipo.contenido.startswith("fosa"):
            nodo.agregar_hijo(self.parsear_lista())
        else:
            nodo.agregar_hijo(self.parsear_expresion())
        return nodo

    # Lista ::= ☾ (Expresion (, Expresion)*)? ☽
    def parsear_lista(self):
        self.consumir("CORCHETE_IZQUIERDO", "☾")
        nodo = NodoASA("Lista", "", "")

        if not self.coincide("CORCHETE_DERECHO"):
            nodo.agregar_hijo(self.parsear_expresion())
            while self.coincide("COMA"):
                self.consumir("COMA")
                nodo.agregar_hijo(self.parsear_expresion())

        self.consumir("CORCHETE_DERECHO", "☽")
        return nodo

    # Asignacion ::= Nombre <- Expresion
    def parsear_asignacion(self):
        tok_nombre = self.consumir("IDENTIFICADOR", "nombre de la variable")
        nodo = NodoASA.desde_token("Asignacion", tok_nombre)

        self.consumir("ASIGNACION", "<-")
        nodo.agregar_hijo(self.parsear_expresion())
        return nodo

    # Condicional ::= "mana" ⟅ ExpresionLogica ⟆ Bloque BloqueSinMana BloqueSin
    # BloqueSinMana ::= "sin mana" ⟅ ExpresionLogica ⟆ Bloque BloqueSinMana | ε
    # BloqueSin ::= "sin" Bloque | ε
    def parsear_condicional(self):
        nodo = NodoASA("Condicional", "", "")

        nodo.agregar_hijo(self.parsear_rama_condicional("MANA", "Mana"))

        while self.coincide("SIN_MANA"):
            nodo.agregar_hijo(
                self.parsear_rama_condicional("SIN_MANA", "SinMana")
            )

        if self.coincide("SIN"):
            tok_sin = self.consumir("SIN")
            rama = NodoASA.desde_token("Sin", tok_sin, "")
            rama.agregar_hijo(self.parsear_bloque())
            nodo.agregar_hijo(rama)

        return nodo

    # Rama con condición (mana o sin mana): palabra ⟅ ExpresionLogica ⟆ Bloque
    def parsear_rama_condicional(self, tipo_token, tipo_nodo):
        tok = self.consumir(tipo_token)
        nodo = NodoASA.desde_token(tipo_nodo, tok, "")

        self.consumir("PARENTESIS_IZQUIERDO", "⟅")
        nodo.agregar_hijo(self.parsear_expresion())
        self.consumir("PARENTESIS_DERECHO", "⟆")

        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    # BucleConvocar ::= "convocar" Tipo Nombre "en" Expresion Bloque
    def parsear_bucle_convocar(self):
        self.consumir("CONVOCAR")

        tipo = self.parsear_tipo()
        tok_nombre = self.consumir("IDENTIFICADOR", "variable del bucle")

        nodo = NodoASA.desde_token("BucleConvocar", tok_nombre)
        nodo.agregar_hijo(tipo)

        self.consumir("EN", "en")
        nodo.agregar_hijo(self.parsear_expresion())

        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    # BuclePersistir ::= "persistir" ⟅ ExpresionLogica ⟆ Bloque
    def parsear_bucle_persistir(self):
        tok = self.consumir("PERSISTIR")
        nodo = NodoASA.desde_token("BuclePersistir", tok, "")

        self.consumir("PARENTESIS_IZQUIERDO", "⟅")
        nodo.agregar_hijo(self.parsear_expresion())
        self.consumir("PARENTESIS_DERECHO", "⟆")

        nodo.agregar_hijo(self.parsear_bloque())
        return nodo
