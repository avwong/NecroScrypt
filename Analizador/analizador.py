"""
Analizador Sintáctico (Parser) para NecroScrypt con Modo Pánico.

Recorre la lista de tokens producida por el Explorador (Scanner) y construye
el Árbol de Sintaxis Abstracta (ASA) verificando la gramática del lenguaje.
"""

from Comun.asa import NodoASA
from Comun.errores import ErrorSintactico
from Comun.gramatica import (
    IDENTIFICADOR_ERRORES,
    INICIOS_DE_DECLARACION,
    TIPOS_PRIMITIVOS,
)
from Comun.tokens import Token


class Analizador:
    """
    Analizador sintáctico descendente recursivo amigable y con recuperación en Modo Pánico.
    """

    INICIOS_DE_DECLARACION = INICIOS_DE_DECLARACION
    TIPOS_PRIMITIVOS = TIPOS_PRIMITIVOS
    IDENTIFICADOR_ERRORES = IDENTIFICADOR_ERRORES

    def __init__(self, lista_tokens):
        """
        Inicializa el analizador sintáctico con la secuencia de tokens.

        Parámetros:
            lista_tokens : Lista de objetos Token provenientes del Explorador.
        """
        self.tokens = list(lista_tokens)
        self.posicion_actual = 0
        self.errores = []

        # Asegurar token EOF como centinela al final
        ult = self.tokens[-1] if self.tokens else None
        if not ult or ult.tipo != "EOF":
            self.tokens.append(Token("EOF", "", ult.linea if ult else 1, ult.columna if ult else 1))

    def consultar(self, distancia=0):
        """
        Mira un token hacia adelante sin consumirlo.

        Parámetros:
            distancia (int): Cantidad de posiciones a adelantar (0 para el token actual).

        Retorna:
            Token: El token en esa posición, o el token EOF si se llega al final.
        """
        idx = self.posicion_actual + distancia
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def coincide(self, *tipos_esperados):
        """
        Verifica si el token actual es de alguno de los tipos esperados.

        Parámetros:
            *tipos_esperados (str): Nombres de los tipos de token a comprobar.

        Retorna:
            bool: True si el token actual coincide con alguno, False en caso contrario.
        """
        return self.consultar().tipo in tipos_esperados

    def describir_token(self, token):
        """
        Devuelve un texto entendible para mostrar el token en los errores.

        Parámetros:
            token (Token): El token que se quiere describir.

        Retorna:
            str: Nombre amigable o contenido visible del token.
        """
        if token.tipo == "EOF":
            return "fin de archivo"
        return token.contenido if token.contenido != "" else self.IDENTIFICADOR_ERRORES.get(token.tipo, token.tipo)

    def describir_esperado(self, esperado=""):
        """
        Traduce el identificador interno esperado a un texto más claro.

        Parámetros:
            esperado (str): Nombre interno del token esperado (ejemplo: 'FIN_INSTRUCCION').

        Retorna:
            str: Símbolo o palabra legible (ejemplo: '☩').
        """
        return self.IDENTIFICADOR_ERRORES.get(esperado, esperado) if esperado else ""

    def registrar_error(self, esperado="", mensaje=None, token=None):
        """
        Crea, guarda y retorna un error sintáctico detallado.

        Parámetros:
            esperado (str): Lo que la gramática esperaba encontrar.
            mensaje (str, opcional): Mensaje explicativo personalizado.
            token (Token, opcional): Token donde ocurrió el fallo (por defecto el actual).

        Retorna:
            ErrorSintactico: El objeto de error registrado en la lista.
        """
        tok = token or self.consultar()
        err = ErrorSintactico(tok.linea, tok.columna, mensaje=mensaje) if mensaje is not None else \
            ErrorSintactico(tok.linea, tok.columna, esperado=self.describir_esperado(esperado), encontrado=self.describir_token(tok))
        self.errores.append(err)
        return err

    def consumir(self, tipo_esperado=None, contexto=""):
        """
        Avanza un token si coincide con lo esperado, o registra un error sin mover el cursor.

        Parámetros:
            tipo_esperado (str, opcional): Tipo de token que se espera recibir.
            contexto (str, opcional): Descripción de la regla o elemento en curso.

        Retorna:
            Token: El token leído.
        """
        tok = self.consultar()
        if tipo_esperado and tok.tipo != tipo_esperado:
            self.registrar_error(esperado=tipo_esperado, token=tok)
            return tok
        self.posicion_actual += 1
        return tok

    def consumir_con_panico(self, tipo_esperado, nombre_esperado=None):
        """
        Exige un token y, si no aparece, activa el Modo Pánico para recuperarse.

        Parámetros:
            tipo_esperado (str): Tipo de token requerido obligatoriamente.
            nombre_esperado (str, opcional): Nombre amigable para el mensaje de error.

        Retorna:
            Token: El token consumido, o None si no se encontró y se recuperó.
        """
        if not self.coincide(tipo_esperado):
            self.registrar_error(esperado=nombre_esperado or tipo_esperado)
            self.recuperar_modo_panico()
            return None
        return self.consumir()

    def recuperar_modo_panico(self):
        """
        Descarta tokens dañados hasta encontrar un delimitador seguro ('☩' o '✧').

        Retorna:
            None
        """
        while not self.coincide("EOF", "FIN_BLOQUE"):
            if self.consumir().tipo == "FIN_INSTRUCCION":
                return

    def exigir_fin_instruccion(self):
        """
        Verifica el cierre de la instrucción con '☩' y sincroniza si falta.

        Retorna:
            Token: El token '☩' consumido, o None si faltaba.
        """
        if self.coincide("FIN_INSTRUCCION"):
            return self.consumir()

        tok = self.consultar()
        self.registrar_error(esperado="☩", token=tok)
        inicios = self.INICIOS_DE_DECLARACION + (
            "MANA", "CONVOCAR", "PERSISTIR", "SACRIFICAR",
            "INVOCAR", "REVIVIR", "COMENTARIO", "IDENTIFICADOR", "FIN_BLOQUE"
        )
        if tok.tipo not in inicios:
            self.recuperar_modo_panico()

    def analizar(self):
        """
        Inicia el análisis sintáctico de todo el código fuente.

        Retorna:
            NodoASA: Nodo raíz 'Programa' con todos los rituales e instrucciones.
        """
        programa = NodoASA("Programa", "", "")
        while not self.coincide("EOF"):
            elem = self.parsear_elemento()
            if elem:
                programa.agregar_hijo(elem)
        return programa

    def parsear_elemento(self):
        """
        Reconoce si el siguiente elemento es un ritual o una instrucción suelta.

        Retorna:
            NodoASA: Nodo del ritual o instrucción reconocido.
        """
        return self.parsear_ritual() if self.coincide("RITUAL") else self.parsear_instruccion()

    def parsear_ritual(self):
        """
        Parsea una función o ritual completo con sus parámetros y bloque.

        Regla:
            Ritual ::= 'ritual' IDENTIFICADOR '⟅' Parametros '⟆' ('~>' Tipo)? Bloque

        Retorna:
            NodoASA: Nodo de tipo 'Ritual'.
        """
        self.consumir("RITUAL")
        nodo = NodoASA.desde_token("Ritual", self.consumir("IDENTIFICADOR", "nombre del ritual"))

        self.consumir("PARENTESIS_IZQUIERDO")
        nodo.agregar_hijo(self.parsear_parametros())
        self.consumir("PARENTESIS_DERECHO")

        if self.coincide("ASIGNACION_RETORNO"):
            self.consumir("ASIGNACION_RETORNO")
            ret = NodoASA("TipoRetorno", "", "")
            ret.agregar_hijo(self.parsear_tipo())
            nodo.agregar_hijo(ret)

        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    def parsear_elementos_por_comas(self, fn_elemento, token_cierre):
        """
        Lee una lista de elementos separados por comas hasta un delimitador de cierre.

        Parámetros:
            fn_elemento (callable): Función para parsear cada elemento individual.
            token_cierre (str): Tipo de token que marca el fin de la lista.

        Retorna:
            list: Lista de nodos generados.
        """
        elementos = []
        while not self.coincide(token_cierre, "EOF"):
            elem = fn_elemento()
            if elem is not None:
                elementos.append(elem)
            if not self.coincide("COMA"):
                break
            self.consumir("COMA")
        return elementos

    def parsear_lista_nodos(self, nombre_nodo, fn_elemento, token_cierre):
        """
        Construye un nodo contenedor con elementos separados por comas.

        Parámetros:
            nombre_nodo (str): Etiqueta del nodo contenedor (ej: 'Parametros', 'Lista').
            fn_elemento (callable): Función que parsea cada elemento hijo.
            token_cierre (str): Tipo de token que marca el final de la lista.

        Retorna:
            NodoASA: Nodo contenedor con los elementos añadidos como hijos.
        """
        nodo = NodoASA(nombre_nodo, "", "")
        for elem in self.parsear_elementos_por_comas(fn_elemento, token_cierre):
            nodo.agregar_hijo(elem)
        return nodo

    def parsear_parametros(self):
        """
        Parsea los parámetros formales de un ritual entre '⟅' y '⟆'.

        Retorna:
            NodoASA: Nodo 'Parametros' con los parámetros hijos.
        """
        return self.parsear_lista_nodos("Parametros", self.parsear_parametro, "PARENTESIS_DERECHO")

    def parsear_parametro(self):
        """
        Parsea un parámetro individual: tipo de dato y su identificador.

        Regla:
            Parametro ::= Tipo IDENTIFICADOR

        Retorna:
            NodoASA: Nodo 'Parametro'.
        """
        tipo, id_tok = self.parsear_tipo(), self.consumir("IDENTIFICADOR", "nombre del parámetro")
        nodo = NodoASA.desde_token("Parametro", id_tok)
        nodo.agregar_hijo(tipo)
        return nodo

    def parsear_tipo(self):
        """
        Parsea un tipo primitivo (calavera, cantico...) o una fosa (lista).

        Retorna:
            NodoASA: Nodo 'Tipo' con el tipo reconocido.
        """
        if self.coincide("FOSA"):
            tok_fosa = self.consumir("FOSA")
            attr = f"línea = {tok_fosa.linea}, columna = {tok_fosa.columna}"
            if self.coincide("CALAVERA", "CANTICO", "ESENCIA", "LATIDO"):
                return NodoASA("Tipo", f"fosa {self.consumir().contenido}", attr)
            self.registrar_error(mensaje=f"Se esperaba un tipo para la fosa, pero encontré '{self.describir_token(self.consultar())}'", token=tok_fosa)
            return NodoASA("Tipo", "fosa", attr)

        if self.coincide(*self.TIPOS_PRIMITIVOS):
            tok = self.consumir()
            return NodoASA.desde_token("Tipo", tok, tok.contenido)

        tok = self.consultar()
        self.registrar_error(mensaje=f"Se esperaba un tipo de dato, pero encontré '{self.describir_token(tok)}'", token=tok)
        return NodoASA("Tipo", "", f"línea = {tok.linea}, columna = {tok.columna}")

    def parsear_bloque(self):
        """
        Parsea un bloque de instrucciones delimitado entre '✦' y '✧'.

        Retorna:
            NodoASA: Nodo 'Bloque' con sus instrucciones hijas.
        """
        self.consumir("INICIO_BLOQUE")
        bloque = NodoASA("Bloque", "", "")
        while not self.coincide("FIN_BLOQUE", "EOF"):
            instr = self.parsear_instruccion()
            if instr:
                bloque.agregar_hijo(instr)
        self.consumir("FIN_BLOQUE")
        return bloque

    def parsear_instruccion(self):
        """
        Identifica y parsea la siguiente instrucción del lenguaje según su inicio.

        Retorna:
            NodoASA: Nodo de la instrucción parseada, o None si era comentario o hubo error.
        """
        tok, sig = self.consultar(), self.consultar(1)

        # 1. Comentarios sueltos
        if tok.tipo == "COMENTARIO":
            self.consumir("COMENTARIO")
            return None

        # 2. Instrucciones que terminan con fin de instrucción '☩'
        nodo = None
        if self.coincide(*self.INICIOS_DE_DECLARACION):
            nodo = self.parsear_declaracion()
        elif tok.tipo == "IDENTIFICADOR" and sig.tipo == "ASIGNACION":
            nodo = self.parsear_asignacion()
        elif tok.tipo in ("INVOCAR", "REVIVIR") or (tok.tipo == "IDENTIFICADOR" and sig.tipo == "PARENTESIS_IZQUIERDO"):
            nodo = self.parsear_llamada_ritual()
        elif tok.tipo == "SACRIFICAR":
            nodo = self.parsear_sacrificio()
        # 3. Estructuras de control (finalizan en bloque ✧, no llevan ☩)
        elif tok.tipo == "MANA":
            return self.parsear_condicional()
        elif tok.tipo == "CONVOCAR":
            return self.parsear_bucle_convocar()
        elif tok.tipo == "PERSISTIR":
            return self.parsear_bucle_persistir()
        else:
            self.registrar_error(mensaje=f"Se esperaba una instrucción, pero encontré '{self.describir_token(tok)}'")
            self.recuperar_modo_panico()
            return None

        if nodo is not None:
            self.exigir_fin_instruccion()
        return nodo

    def parsear_declaracion(self):
        """
        Parsea la declaración de una variable o fosa con su asignación inicial '<-'.

        Regla:
            Declaracion ::= Tipo IDENTIFICADOR '<-' (Lista | Expresion)

        Retorna:
            NodoASA: Nodo 'Declaracion' con tipo y valor inicial, o None si hay error.
        """
        tipo, tok_id = self.parsear_tipo(), self.consumir_con_panico("IDENTIFICADOR", "un identificador")
        if not tok_id or self.consumir_con_panico("ASIGNACION", "<-") is None:
            return None
        nodo = NodoASA.desde_token("Declaracion", tok_id)
        nodo.agregar_hijo(tipo)
        es_fosa = tipo.contenido.startswith("fosa")
        valor = self.parsear_lista() if es_fosa and self.coincide("CORCHETE_IZQUIERDO") else self.parsear_expresion()
        nodo.agregar_hijo(valor)
        return nodo

    def parsear_lista(self):
        """
        Parsea una lista de expresiones encerrada entre '☾' y '☽'.

        Retorna:
            NodoASA: Nodo 'Lista' con las expresiones contenidas.
        """
        self.consumir("CORCHETE_IZQUIERDO")
        lista = self.parsear_lista_nodos("Lista", self.parsear_expresion, "CORCHETE_DERECHO")
        self.consumir("CORCHETE_DERECHO")
        return lista

    def parsear_asignacion(self):
        """
        Parsea la reasignación de una variable existente (variable <- expresion).

        Retorna:
            NodoASA: Nodo 'Asignacion'.
        """
        nodo = NodoASA.desde_token("Asignacion", self.consumir("IDENTIFICADOR", "nombre de la variable"))
        self.consumir("ASIGNACION")
        nodo.agregar_hijo(self.parsear_expresion())
        return nodo

    def parsear_sacrificio(self):
        """
        Parsea la sentencia de retorno 'sacrificar' con o sin valor de vuelta.

        Retorna:
            NodoASA: Nodo 'Sacrificio'.
        """
        nodo = NodoASA.desde_token("Sacrificio", self.consumir("SACRIFICAR"), "")
        if not self.coincide("FIN_INSTRUCCION", "EOF"):
            expr = self.parsear_expresion()
            if expr:
                nodo.agregar_hijo(expr)
        return nodo

    def parsear_llamada_ritual(self):
        """
        Parsea una llamada a un ritual propio o de sistema ('invocar' / 'revivir').

        Retorna:
            NodoASA: Nodo 'LlamadaRitual' con sus argumentos.
        """
        tok = self.consumir() if self.coincide("INVOCAR", "REVIVIR", "IDENTIFICADOR") else self.consumir("IDENTIFICADOR", "nombre del ritual")
        nodo = NodoASA.desde_token("LlamadaRitual", tok)
        self.consumir("PARENTESIS_IZQUIERDO")
        nodo.agregar_hijo(self.parsear_argumentos())
        self.consumir("PARENTESIS_DERECHO")
        return nodo

    def parsear_argumentos(self):
        """
        Parsea los argumentos pasados en una llamada entre '⟅' y '⟆'.

        Retorna:
            NodoASA: Nodo 'Argumentos'.
        """
        return self.parsear_lista_nodos("Argumentos", self.parsear_argumento, "PARENTESIS_DERECHO")

    def parsear_argumento(self):
        """
        Parsea un único argumento (que puede ser un tipo de dato o una expresión).

        Retorna:
            NodoASA: Nodo con el tipo o la expresión del argumento.
        """
        return self.parsear_tipo() if self.coincide("FOSA", *self.TIPOS_PRIMITIVOS) else self.parsear_expresion()

    def parsear_estructura_con_condicion(self, tipo_nodo, tipo_token):
        """
        Parsea estructuras con el patrón común: PALABRA ⟅ expresion ⟆ Bloque.

        Parámetros:
            tipo_nodo (str): Nombre que llevará el nodo (ejemplo: 'Mana', 'BuclePersistir').
            tipo_token (str): Tipo de token que inicia la estructura (ejemplo: 'MANA').

        Retorna:
            NodoASA: Nodo construido con la condición y el bloque de código.
        """
        nodo = NodoASA.desde_token(tipo_nodo, self.consumir(tipo_token), "")
        self.consumir("PARENTESIS_IZQUIERDO")
        nodo.agregar_hijo(self.parsear_expresion())
        self.consumir("PARENTESIS_DERECHO")
        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    def parsear_condicional(self):
        """
        Parsea la estructura condicional completa: mana, sin mana* y sin?.

        Retorna:
            NodoASA: Nodo 'Condicional' con todas sus ramas.
        """
        nodo = NodoASA("Condicional", "", "")
        nodo.agregar_hijo(self.parsear_estructura_con_condicion("Mana", "MANA"))
        while self.coincide("SIN_MANA"):
            nodo.agregar_hijo(self.parsear_estructura_con_condicion("SinMana", "SIN_MANA"))
        if self.coincide("SIN"):
            sin = NodoASA.desde_token("Sin", self.consumir("SIN"), "")
            sin.agregar_hijo(self.parsear_bloque())
            nodo.agregar_hijo(sin)
        return nodo

    def parsear_bucle_persistir(self):
        """
        Parsea un bucle mientras ('persistir').

        Retorna:
            NodoASA: Nodo 'BuclePersistir'.
        """
        return self.parsear_estructura_con_condicion("BuclePersistir", "PERSISTIR")

    def parsear_bucle_convocar(self):
        """
        Parsea un bucle de iteración sobre colecciones ('convocar').

        Regla:
            BucleConvocar ::= 'convocar' Tipo IDENTIFICADOR 'en' Expresion Bloque

        Retorna:
            NodoASA: Nodo 'BucleConvocar'.
        """
        self.consumir("CONVOCAR")
        tipo, tok_id = self.parsear_tipo(), self.consumir("IDENTIFICADOR", "variable del bucle")
        nodo = NodoASA.desde_token("BucleConvocar", tok_id)
        nodo.agregar_hijo(tipo)
        self.consumir("EN")
        nodo.agregar_hijo(self.parsear_expresion())
        nodo.agregar_hijo(self.parsear_bloque())
        return nodo

    def parsear_operacion_binaria(self, fn_subnivel, tipos_operadores, tipo_nodo):
        """
        Agrupa operaciones binarias por la izquierda respetando la precedencia.

        Parámetros:
            fn_subnivel (callable): Función para parsear el siguiente nivel de precedencia.
            tipos_operadores (tuple): Tipos de token que actúan como operadores.
            tipo_nodo (str): Nombre para el nodo del árbol (ej: 'OperacionAritmetica').

        Retorna:
            NodoASA: Árbol con las operaciones agrupadas.
        """
        izq = fn_subnivel()
        while self.coincide(*tipos_operadores):
            op, der = self.consumir(), fn_subnivel()
            nodo_op = NodoASA(tipo_nodo, op.contenido, f"línea = {op.linea}, columna = {op.columna}")
            nodo_op.agregar_hijo(izq)
            nodo_op.agregar_hijo(der)
            izq = nodo_op
        return izq

    def parsear_expresion(self):
        """
        Nivel 1 de precedencia: Disyunción lógica 'o'.

        Retorna:
            NodoASA: Expresión lógica resultante.
        """
        return self.parsear_operacion_binaria(self.parsear_logica_y, ("O",), "OperacionLogica")

    def parsear_logica_y(self):
        """
        Nivel 2 de precedencia: Conjunción lógica 'y'.

        Retorna:
            NodoASA: Expresión lógica resultante.
        """
        return self.parsear_operacion_binaria(self.parsear_comparacion, ("Y",), "OperacionLogica")

    def parsear_comparacion(self):
        """
        Nivel 3 de precedencia: Operaciones relacionales (==, !=, <, >, <=, >=).

        Retorna:
            NodoASA: Nodo 'Comparacion' o la subexpresión si no hay operador relacional.
        """
        izq = self.parsear_suma_resta()
        ops = ("IGUAL_QUE", "DIFERENTE_QUE", "MENOR_QUE", "MAYOR_QUE", "MENOR_IGUAL", "MAYOR_IGUAL")
        if self.coincide(*ops):
            op, der = self.consumir(), self.parsear_suma_resta()
            nodo_op = NodoASA("Comparacion", op.contenido, f"línea = {op.linea}, columna = {op.columna}")
            nodo_op.agregar_hijo(izq)
            nodo_op.agregar_hijo(der)
            return nodo_op
        return izq

    def parsear_suma_resta(self):
        """
        Nivel 4 de precedencia: Suma ('ensamblar') y resta ('mutilar').

        Retorna:
            NodoASA: Expresión aritmética resultante.
        """
        return self.parsear_operacion_binaria(self.parsear_producto, ("ENSAMBLAR", "MUTILAR"), "OperacionAritmetica")

    def parsear_producto(self):
        """
        Nivel 5 de precedencia: Multiplicación ('infestar'), división ('desmembrar') y residuo ('restos').

        Retorna:
            NodoASA: Expresión aritmética resultante.
        """
        return self.parsear_operacion_binaria(self.parsear_primaria, ("INFESTAR", "DESMEMBRAR", "RESTOS"), "OperacionAritmetica")

    def parsear_primaria(self):
        """
        Nivel 6 de precedencia: Literales, variables, llamadas y expresiones entre '⟅' y '⟆'.

        Retorna:
            NodoASA: Nodo del elemento atómico, o None si no es una expresión válida.
        """
        tok = self.consultar()

        # 1. Llamada a ritual
        if tok.tipo in ("INVOCAR", "REVIVIR") or (tok.tipo == "IDENTIFICADOR" and self.consultar(1).tipo == "PARENTESIS_IZQUIERDO"):
            return self.parsear_llamada_ritual()

        # 2. Literales y variables simples
        mapa = {"ENTERO": "Entero", "DECIMAL": "Decimal", "IDENTIFICADOR": "Identificador", "VIVO": "Booleano", "MUERTO": "Booleano", "CENIZA": "Ceniza"}
        if tok.tipo in mapa:
            return NodoASA.desde_token(mapa[self.consumir().tipo], tok)

        # 3. Cadenas de texto
        if tok.tipo == "CADENA":
            return NodoASA.desde_token("Cadena", self.consumir("CADENA"), tok.contenido[1:-1])

        # 4. Expresión agrupada entre paréntesis
        if tok.tipo == "PARENTESIS_IZQUIERDO":
            self.consumir("PARENTESIS_IZQUIERDO")
            expr = self.parsear_expresion()
            self.consumir("PARENTESIS_DERECHO")
            return expr

        # 5. Error si no es una expresión válida
        self.registrar_error(mensaje=f"Se esperaba una expresión, pero encontré '{self.describir_token(tok)}'")
        if tok.tipo != "EOF":
            self.consumir()
        return None
