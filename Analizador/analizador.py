"""
Analizador Sintáctico (Parser) de NecroScrypt con Modo Pánico.

Recibe la lista de tokens producida por el Explorador (Scanner) y construye
el Árbol de Sintaxis Abstracta (ASA) verificando la gramática del lenguaje.
"""

from Comun.asa import NodoASA
from Comun.errores import ErrorSintactico
from Comun.gramatica import (
    INICIOS_DE_DECLARACION,
    NOMBRES_AMIGABLES,
    TIPOS_PRIMITIVOS,
)
from Comun.tokens import Token


class Analizador:
    """
    Analizador sintáctico descendente recursivo para NecroScrypt.
    Diseñado de forma clara y directa para principiantes en Python.
    """

    INICIOS_DE_DECLARACION = INICIOS_DE_DECLARACION
    TIPOS_PRIMITIVOS = TIPOS_PRIMITIVOS
    NOMBRES_AMIGABLES = NOMBRES_AMIGABLES

    def __init__(self, lista_tokens):
        self.tokens = list(lista_tokens)
        self.posicion_actual = 0
        self.errores = []

        # Asegurar token EOF al final
        if not self.tokens:
            self.tokens.append(Token("EOF", "", 1, 1))
        elif self.tokens[-1].tipo != "EOF":
            ultimo = self.tokens[-1]
            self.tokens.append(Token("EOF", "", ultimo.linea, ultimo.columna))

    @property
    def pos(self):
        """Cursor de posición actual."""
        return self.posicion_actual

    # -------------------------------------------------------------------------
    # Navegación de tokens, reporte de errores y Modo Pánico
    # -------------------------------------------------------------------------

    def consultar(self, distancia=0):
        """Mira un token hacia adelante sin consumirlo."""
        indice = self.posicion_actual + distancia
        if indice < len(self.tokens):
            return self.tokens[indice]
        return self.tokens[-1]

    def coincide(self, *tipos_esperados):
        """Comprueba si el token actual es de alguno de los tipos esperados."""
        return self.consultar().tipo in tipos_esperados

    def describir_token(self, token):
        """Devuelve un nombre legible para mostrar en los mensajes de error."""
        if token.tipo == "EOF":
            return "fin de archivo"
        if token.contenido != "":
            return token.contenido
        return self.NOMBRES_AMIGABLES.get(token.tipo, token.tipo)

    def describir_esperado(self, esperado=""):
        """Devuelve un nombre amigable para lo que se esperaba."""
        if not esperado:
            return ""
        return self.NOMBRES_AMIGABLES.get(esperado, esperado)

    def registrar_error(self, esperado="", mensaje=None, token=None):
        """Crea y registra un error sintáctico con formato claro."""
        tok = token or self.consultar()
        if mensaje is not None:
            err = ErrorSintactico(linea=tok.linea, columna=tok.columna, mensaje=mensaje)
        else:
            esp = self.describir_esperado(esperado)
            enc = self.describir_token(tok)
            err = ErrorSintactico(linea=tok.linea, columna=tok.columna, esperado=esp, encontrado=enc)
        self.errores.append(err)
        return err

    def consumir(self, tipo_esperado=None, contexto=""):
        """Consume el token actual si coincide; si no, anota error sin avanzar."""
        token_actual = self.consultar()
        if tipo_esperado is not None and token_actual.tipo != tipo_esperado:
            self.registrar_error(esperado=tipo_esperado, token=token_actual)
            return token_actual
        self.posicion_actual += 1
        return token_actual

    def consumir_con_panico(self, tipo_esperado, nombre_esperado=None):
        """Consume el token esperado o activa el modo pánico si falta."""
        if not self.coincide(tipo_esperado):
            self.registrar_error(esperado=nombre_esperado or tipo_esperado)
            self.recuperar_modo_panico()
            return None
        return self.consumir()

    def recuperar_modo_panico(self):
        """Descarta tokens hasta encontrar fin de instrucción '☩' o de bloque '✧'."""
        while not self.coincide("EOF"):
            token_actual = self.consultar()
            if token_actual.tipo == "FIN_INSTRUCCION":
                self.posicion_actual += 1
                return
            if token_actual.tipo == "FIN_BLOQUE":
                return
            self.posicion_actual += 1

    def exigir_fin_instruccion(self):
        """Exige '☩' al final de la instrucción y sincroniza con modo pánico si falta."""
        if self.coincide("FIN_INSTRUCCION"):
            self.consumir("FIN_INSTRUCCION")
            return

        token_actual = self.consultar()
        self.registrar_error(esperado="☩", token=token_actual)

        inicios = self.INICIOS_DE_DECLARACION + (
            "MANA", "CONVOCAR", "PERSISTIR", "SACRIFICAR",
            "INVOCAR", "REVIVIR", "COMENTARIO", "IDENTIFICADOR"
        )
        if token_actual.tipo not in inicios and token_actual.tipo != "FIN_BLOQUE":
            self.recuperar_modo_panico()

    # -------------------------------------------------------------------------
    # Programa, rituales y tipos
    # -------------------------------------------------------------------------

    def analizar(self):
        """Punto de entrada: analiza todo el archivo y devuelve el nodo Programa."""
        nodo_programa = NodoASA("Programa", "", "")
        while not self.coincide("EOF"):
            elemento = self.parsear_elemento()
            if elemento is not None:
                nodo_programa.agregar_hijo(elemento)
        return nodo_programa

    def parsear_elemento(self):
        """Elemento ::= Ritual | Instruccion"""
        if self.coincide("RITUAL"):
            return self.parsear_ritual()
        return self.parsear_instruccion()

    def parsear_ritual(self):
        """Ritual ::= 'ritual' IDENTIFICADOR '⟅' Parametros '⟆' TipoRetorno? Bloque"""
        self.consumir("RITUAL")
        token_nombre = self.consumir("IDENTIFICADOR", "nombre del ritual")
        nodo_ritual = NodoASA.desde_token("Ritual", token_nombre)

        self.consumir("PARENTESIS_IZQUIERDO")
        nodo_ritual.agregar_hijo(self.parsear_parametros())
        self.consumir("PARENTESIS_DERECHO")

        if self.coincide("ASIGNACION_RETORNO"):
            self.consumir("ASIGNACION_RETORNO")
            nodo_retorno = NodoASA("TipoRetorno", "", "")
            nodo_retorno.agregar_hijo(self.parsear_tipo())
            nodo_ritual.agregar_hijo(nodo_retorno)

        nodo_ritual.agregar_hijo(self.parsear_bloque())
        return nodo_ritual

    def parsear_elementos_por_comas(self, fn_parsear_elemento, token_cierre):
        """Lee elementos separados por comas hasta encontrar el token de cierre."""
        elementos = []
        if not self.coincide(token_cierre):
            elem = fn_parsear_elemento()
            if elem is not None:
                elementos.append(elem)
            while self.coincide("COMA"):
                self.consumir("COMA")
                sig = fn_parsear_elemento()
                if sig is not None:
                    elementos.append(sig)
        return elementos

    def parsear_parametros(self):
        """Parametros ::= (Parametro (',' Parametro)*)?"""
        nodo = NodoASA("Parametros", "", "")
        for param in self.parsear_elementos_por_comas(self.parsear_parametro, "PARENTESIS_DERECHO"):
            nodo.agregar_hijo(param)
        return nodo

    def parsear_parametro(self):
        """Parametro ::= Tipo IDENTIFICADOR"""
        nodo_tipo = self.parsear_tipo()
        token_nombre = self.consumir("IDENTIFICADOR", "nombre del parámetro")
        nodo = NodoASA.desde_token("Parametro", token_nombre)
        nodo.agregar_hijo(nodo_tipo)
        return nodo

    def parsear_tipo(self):
        """Tipo ::= TipoPrimitivo | 'fosa' TipoPrimitivo"""
        if self.coincide("FOSA"):
            token_fosa = self.consumir("FOSA")
            attr = f"línea = {token_fosa.linea}, columna = {token_fosa.columna}"
            if self.coincide("CALAVERA", "CANTICO", "ESENCIA", "LATIDO"):
                subtipo = self.consumir()
                return NodoASA("Tipo", f"fosa {subtipo.contenido}", attr)
            self.registrar_error(mensaje=f"Se esperaba un tipo para la fosa, pero encontré '{self.describir_token(self.consultar())}'", token=token_fosa)
            return NodoASA("Tipo", "fosa", attr)

        if self.coincide("CALAVERA", "CANTICO", "ESENCIA", "LATIDO", "CENIZA"):
            tok = self.consumir()
            return NodoASA.desde_token("Tipo", tok, tok.contenido)

        actual = self.consultar()
        self.registrar_error(mensaje=f"Se esperaba un tipo de dato, pero encontré '{self.describir_token(actual)}'", token=actual)
        return NodoASA("Tipo", "", f"línea = {actual.linea}, columna = {actual.columna}")

    def parsear_bloque(self):
        """Bloque ::= '✦' Instruccion* '✧'"""
        self.consumir("INICIO_BLOQUE")
        nodo_bloque = NodoASA("Bloque", "", "")
        while not self.coincide("FIN_BLOQUE", "EOF"):
            instruccion = self.parsear_instruccion()
            if instruccion is not None:
                nodo_bloque.agregar_hijo(instruccion)
        self.consumir("FIN_BLOQUE")
        return nodo_bloque

    # -------------------------------------------------------------------------
    # Instrucciones
    # -------------------------------------------------------------------------

    def parsear_instruccion(self):
        """Instruccion ::= Declaracion | Asignacion | LlamadaRitual | Sacrificio | Condicional | Bucle"""
        token = self.consultar()
        if token.tipo == "COMENTARIO":
            self.consumir("COMENTARIO")
            return None

        # Declaración: tipo identificador <- ...
        if self.coincide(*self.INICIOS_DE_DECLARACION):
            nodo = self.parsear_declaracion()
            if nodo is not None:
                self.exigir_fin_instruccion()
            return nodo

        # Asignación: variable <- ...
        siguiente = self.consultar(1)
        if token.tipo == "IDENTIFICADOR" and siguiente.tipo == "ASIGNACION":
            nodo = self.parsear_asignacion()
            self.exigir_fin_instruccion()
            return nodo

        # Llamada como instrucción: invocar(...) ☩ o ritual(...) ☩
        es_llamada_sistema = token.tipo in ("INVOCAR", "REVIVIR")
        es_llamada_usuario = token.tipo == "IDENTIFICADOR" and siguiente.tipo == "PARENTESIS_IZQUIERDO"
        if es_llamada_sistema or es_llamada_usuario:
            nodo = self.parsear_llamada_ritual()
            self.exigir_fin_instruccion()
            return nodo

        # Sacrificio (retorno): sacrificar expr ☩
        if token.tipo == "SACRIFICAR":
            nodo = self.parsear_sacrificio()
            self.exigir_fin_instruccion()
            return nodo

        # Estructuras de control (no llevan ☩ porque terminan en bloque ✧)
        if token.tipo == "MANA":
            return self.parsear_condicional()
        if token.tipo == "CONVOCAR":
            return self.parsear_bucle_convocar()
        if token.tipo == "PERSISTIR":
            return self.parsear_bucle_persistir()

        # Error si no es ninguna instrucción conocida
        self.registrar_error(mensaje=f"Se esperaba una instrucción, pero encontré '{self.describir_token(token)}'")
        self.recuperar_modo_panico()
        return None

    def parsear_declaracion(self):
        """Declaracion ::= Tipo IDENTIFICADOR '<-' (Lista | Expresion)"""
        nodo_tipo = self.parsear_tipo()
        token_nombre = self.consumir_con_panico("IDENTIFICADOR", "un identificador")
        if token_nombre is None:
            return None

        nodo_decl = NodoASA.desde_token("Declaracion", token_nombre)
        nodo_decl.agregar_hijo(nodo_tipo)

        if self.consumir_con_panico("ASIGNACION", "<-") is None:
            return None

        es_fosa = nodo_tipo.contenido.startswith("fosa")
        if es_fosa and self.coincide("CORCHETE_IZQUIERDO"):
            valor = self.parsear_lista()
        else:
            valor = self.parsear_expresion()

        nodo_decl.agregar_hijo(valor)
        return nodo_decl

    def parsear_lista(self):
        """Lista ::= '☾' (Expresion (',' Expresion)*)? '☽'"""
        self.consumir("CORCHETE_IZQUIERDO")
        nodo_lista = NodoASA("Lista", "", "")
        for elem in self.parsear_elementos_por_comas(self.parsear_expresion, "CORCHETE_DERECHO"):
            nodo_lista.agregar_hijo(elem)
        self.consumir("CORCHETE_DERECHO")
        return nodo_lista

    def parsear_asignacion(self):
        """Asignacion ::= IDENTIFICADOR '<-' Expresion"""
        token_nombre = self.consumir("IDENTIFICADOR", "nombre de la variable")
        nodo_asignacion = NodoASA.desde_token("Asignacion", token_nombre)
        self.consumir("ASIGNACION")
        nodo_asignacion.agregar_hijo(self.parsear_expresion())
        return nodo_asignacion

    def parsear_sacrificio(self):
        """Sacrificio ::= 'sacrificar' Expresion?"""
        token_sacrificio = self.consumir("SACRIFICAR")
        nodo_sacrificio = NodoASA.desde_token("Sacrificio", token_sacrificio, "")
        if not self.coincide("FIN_INSTRUCCION", "EOF"):
            expr = self.parsear_expresion()
            if expr is not None:
                nodo_sacrificio.agregar_hijo(expr)
        return nodo_sacrificio

    def parsear_llamada_ritual(self):
        """LlamadaRitual ::= IDENTIFICADOR '⟅' Argumentos '⟆'"""
        if self.coincide("INVOCAR", "REVIVIR", "IDENTIFICADOR"):
            token_nombre = self.consumir()
        else:
            token_nombre = self.consumir("IDENTIFICADOR", "nombre del ritual")

        nodo_llamada = NodoASA.desde_token("LlamadaRitual", token_nombre)
        self.consumir("PARENTESIS_IZQUIERDO")
        nodo_llamada.agregar_hijo(self.parsear_argumentos())
        self.consumir("PARENTESIS_DERECHO")
        return nodo_llamada

    def parsear_argumentos(self):
        """Argumentos ::= (Argumento (',' Argumento)*)?"""
        nodo = NodoASA("Argumentos", "", "")
        for arg in self.parsear_elementos_por_comas(self.parsear_argumento, "PARENTESIS_DERECHO"):
            nodo.agregar_hijo(arg)
        return nodo

    def parsear_argumento(self):
        """Argumento ::= Tipo | Expresion"""
        if self.coincide("FOSA", *self.TIPOS_PRIMITIVOS):
            return self.parsear_tipo()
        return self.parsear_expresion()

    # -------------------------------------------------------------------------
    # Condicionales y Bucles
    # -------------------------------------------------------------------------

    def parsear_estructura_con_condicion(self, tipo_nodo, tipo_token):
        """Parsea estructuras con el patrón: PALABRA ⟅ expresion ⟆ Bloque"""
        token = self.consumir(tipo_token)
        nodo = NodoASA.desde_token(tipo_nodo, token, "")
        self.consumir("PARENTESIS_IZQUIERDO")
        nodo.agregar_hijo(self.parsear_expresion())
        self.consumir("PARENTESIS_DERECHO")
        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    def parsear_condicional(self):
        """Condicional ::= Mana SinMana* Sin?"""
        nodo_condicional = NodoASA("Condicional", "", "")
        nodo_condicional.agregar_hijo(self.parsear_estructura_con_condicion("Mana", "MANA"))

        while self.coincide("SIN_MANA"):
            nodo_condicional.agregar_hijo(self.parsear_estructura_con_condicion("SinMana", "SIN_MANA"))

        if self.coincide("SIN"):
            token_sin = self.consumir("SIN")
            nodo_sin = NodoASA.desde_token("Sin", token_sin, "")
            nodo_sin.agregar_hijo(self.parsear_bloque())
            nodo_condicional.agregar_hijo(nodo_sin)

        return nodo_condicional

    def parsear_bucle_persistir(self):
        """BuclePersistir ::= 'persistir' '⟅' Expresion '⟆' Bloque"""
        return self.parsear_estructura_con_condicion("BuclePersistir", "PERSISTIR")

    def parsear_bucle_convocar(self):
        """BucleConvocar ::= 'convocar' Tipo IDENTIFICADOR 'en' Expresion Bloque"""
        self.consumir("CONVOCAR")
        nodo_tipo = self.parsear_tipo()
        token_nombre = self.consumir("IDENTIFICADOR", "variable del bucle")

        nodo_bucle = NodoASA.desde_token("BucleConvocar", token_nombre)
        nodo_bucle.agregar_hijo(nodo_tipo)
        self.consumir("EN")
        nodo_bucle.agregar_hijo(self.parsear_expresion())
        nodo_bucle.agregar_hijo(self.parsear_bloque())
        return nodo_bucle

    # -------------------------------------------------------------------------
    # Expresiones y Precedencia de Operadores
    # -------------------------------------------------------------------------

    def parsear_operacion_binaria(self, fn_subnivel, tipos_operadores, tipo_nodo):
        """Agrupa operaciones binarias por la izquierda (ej: a + b - c)."""
        nodo_izq = fn_subnivel()
        while self.coincide(*tipos_operadores):
            op = self.consumir()
            nodo_der = fn_subnivel()
            nodo_op = NodoASA(tipo_nodo, op.contenido, f"línea = {op.linea}, columna = {op.columna}")
            nodo_op.agregar_hijo(nodo_izq)
            nodo_op.agregar_hijo(nodo_der)
            nodo_izq = nodo_op
        return nodo_izq

    def parsear_expresion(self):
        """Nivel 1: Disyunción lógica 'o'."""
        return self.parsear_operacion_binaria(self.parsear_logica_y, ("O",), "OperacionLogica")

    def parsear_logica_y(self):
        """Nivel 2: Conjunción lógica 'y'."""
        return self.parsear_operacion_binaria(self.parsear_comparacion, ("Y",), "OperacionLogica")

    def parsear_comparacion(self):
        """Nivel 3: Comparaciones relacionales (==, !=, <, >, <=, >=)."""
        nodo_izq = self.parsear_suma_resta()
        operadores = (
            "IGUAL_QUE", "DIFERENTE_QUE", "MENOR_QUE",
            "MAYOR_QUE", "MENOR_IGUAL", "MAYOR_IGUAL",
        )
        if self.coincide(*operadores):
            op = self.consumir()
            nodo_der = self.parsear_suma_resta()
            nodo_op = NodoASA("Comparacion", op.contenido, f"línea = {op.linea}, columna = {op.columna}")
            nodo_op.agregar_hijo(nodo_izq)
            nodo_op.agregar_hijo(nodo_der)
            return nodo_op
        return nodo_izq

    def parsear_suma_resta(self):
        """Nivel 4: Suma ('ensamblar') y resta ('mutilar')."""
        return self.parsear_operacion_binaria(
            self.parsear_producto, ("ENSAMBLAR", "MUTILAR"), "OperacionAritmetica"
        )

    def parsear_producto(self):
        """Nivel 5: Multiplicación ('infestar'), división ('desmembrar'), módulo ('restos')."""
        return self.parsear_operacion_binaria(
            self.parsear_primaria, ("INFESTAR", "DESMEMBRAR", "RESTOS"), "OperacionAritmetica"
        )

    def parsear_primaria(self):
        """Nivel 6: Literales, variables, llamadas y expresiones entre ⟅ ⟆."""
        token = self.consultar()

        # Llamada a ritual
        es_llamada_sistema = token.tipo in ("INVOCAR", "REVIVIR")
        es_llamada_usuario = token.tipo == "IDENTIFICADOR" and self.consultar(1).tipo == "PARENTESIS_IZQUIERDO"
        if es_llamada_sistema or es_llamada_usuario:
            return self.parsear_llamada_ritual()

        # Literales y variables simples
        mapa_literales = {
            "ENTERO": "Entero",
            "DECIMAL": "Decimal",
            "IDENTIFICADOR": "Identificador",
            "VIVO": "Booleano",
            "MUERTO": "Booleano",
            "CENIZA": "Ceniza",
        }
        if token.tipo in mapa_literales:
            self.consumir()
            return NodoASA.desde_token(mapa_literales[token.tipo], token)

        if token.tipo == "CADENA":
            self.consumir("CADENA")
            return NodoASA.desde_token("Cadena", token, token.contenido[1:-1])

        # Expresión agrupada entre paréntesis ⟅ ... ⟆
        if token.tipo == "PARENTESIS_IZQUIERDO":
            self.consumir("PARENTESIS_IZQUIERDO")
            expr = self.parsear_expresion()
            self.consumir("PARENTESIS_DERECHO")
            return expr

        # Error si no es una expresión válida
        self.registrar_error(mensaje=f"Se esperaba una expresión, pero encontré '{self.describir_token(token)}'")
        if token.tipo != "EOF":
            self.consumir()
        return None
