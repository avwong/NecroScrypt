"""
Motor de inferencia de tipos de NecroScrypt.

Recorre las expresiones del ASA, calcula el tipo de cada una, lo guarda en
nodo.tipo_inferido (decorado) y reporta los errores semánticos de tipos:
operaciones inválidas (cantico ensamblar calavera), asignaciones y retornos
con tipos incompatibles, y argumentos con el tipo equivocado.

Esta clase NO recorre las instrucciones ni administra los ámbitos: eso le
corresponde al verificador principal, que la usa así:

    inferencia = InferenciaTipos(tabla, errores)
    inferencia.verificar_declaracion(nodo_declaracion)
    inferencia.verificar_asignacion(nodo_asignacion)
    inferencia.verificar_sacrificio(nodo_sacrificio, tipo_retorno_del_ritual)
    inferencia.exigir_latido(nodo_condicion, "mana")

La tabla solo necesita cumplir el contrato de Comun/simbolos.py (buscar).
"""

from Comun import tipos
from Comun.errores import ErrorSemantico
from Comun.simbolos import RITUAL
from Comun.visitante import Visitante


# Tipo de retorno de los rituales del ambiente estándar cuando no están
# registrados en la tabla de símbolos. None indica que depende de los argumentos.
RITUALES_ESTANDAR = {
    "invocar": tipos.CENIZA,
    "invocar_sin_salto": tipos.CENIZA,
    "revivir": None,
    "mundo": tipos.tipo_fosa(tipos.CALAVERA),
    "insertar": tipos.CENIZA,
    "extraer": None,
    "buscar": tipos.CALAVERA,
}

# Nombres legibles de los operadores para los mensajes de error
DESCRIPCION_OPERADOR = {
    "ensamblar": "ensamblar (suma)",
    "mutilar": "mutilar (resta)",
    "infestar": "infestar (multiplicación)",
    "desmembrar": "desmembrar (división)",
    "restos": "restos (residuo)",
    "y": "y",
    "o": "o",
}


class InferenciaTipos(Visitante):
    """
    Visitante que infiere y valida los tipos de las expresiones del ASA.

    Cada método visitar_<Expresion> retorna el tipo calculado (str) y lo deja
    guardado en nodo.tipo_inferido.
    """

    def __init__(self, tabla, errores=None):
        """
        Parámetros:
            tabla: Objeto con el método buscar(nombre) -> Simbolo o None.
            errores (list, opcional): Lista donde se agregan los ErrorSemantico.
        """
        self.tabla = tabla
        self.errores = errores if errores is not None else []

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def inferir(self, nodo):
        """
        Infiere el tipo de una expresión y decora todo su subárbol.

        Retorna:
            str: Tipo de la expresión, o DESCONOCIDO si el nodo es None.
        """
        if nodo is None:
            return tipos.DESCONOCIDO
        tipo = self.visitar(nodo)
        return tipo if tipo is not None else tipos.DESCONOCIDO

    def reportar(self, nodo, mensaje):
        """Registra un error semántico en la posición del nodo."""
        linea, columna = nodo.posicion()
        error = ErrorSemantico(linea, columna, mensaje)
        self.errores.append(error)
        return error

    @staticmethod
    def decorar(nodo, tipo):
        """Guarda el tipo en el nodo y lo retorna."""
        nodo.tipo_inferido = tipo
        return tipo

    # ------------------------------------------------------------------
    # Literales
    # ------------------------------------------------------------------

    def visitar_Entero(self, nodo):
        return self.decorar(nodo, tipos.CALAVERA)

    def visitar_Decimal(self, nodo):
        return self.decorar(nodo, tipos.ESENCIA)

    def visitar_Cadena(self, nodo):
        return self.decorar(nodo, tipos.CANTICO)

    def visitar_Booleano(self, nodo):
        return self.decorar(nodo, tipos.LATIDO)

    def visitar_Ceniza(self, nodo):
        return self.decorar(nodo, tipos.CENIZA)

    def visitar_Lista(self, nodo):
        """
        Una fosa literal ☾a, b, c☽ debe ser homogénea. Si mezcla calavera y
        esencia, la fosa completa se considera de esencia.
        """
        tipos_elementos = [self.inferir(hijo) for hijo in nodo.hijos]
        conocidos = [t for t in tipos_elementos if t != tipos.DESCONOCIDO]

        if not tipos_elementos:
            return self.decorar(nodo, tipos.FOSA_VACIA)
        if not conocidos:
            return self.decorar(nodo, tipos.DESCONOCIDO)

        if all(tipos.es_numerico(t) for t in conocidos) and tipos.ESENCIA in conocidos:
            return self.decorar(nodo, tipos.tipo_fosa(tipos.ESENCIA))

        primero = conocidos[0]
        for hijo, tipo in zip(nodo.hijos, tipos_elementos):
            if tipo not in (primero, tipos.DESCONOCIDO):
                self.reportar(
                    hijo,
                    f"Una fosa solo puede guardar elementos del mismo tipo: "
                    f"se esperaba {primero} pero se encontró {tipo}",
                )
                return self.decorar(nodo, tipos.tipo_fosa(primero))
        return self.decorar(nodo, tipos.tipo_fosa(primero))

    # ------------------------------------------------------------------
    # Identificadores y llamadas
    # ------------------------------------------------------------------

    def visitar_Identificador(self, nodo):
        """
        El tipo de una variable sale de la tabla de símbolos. Si no existe, el
        error de "no declarada" lo reporta la tabla; aquí queda DESCONOCIDO.
        """
        simbolo = self.tabla.buscar(nodo.contenido)
        if simbolo is None:
            return self.decorar(nodo, tipos.DESCONOCIDO)
        if simbolo.categoria == RITUAL:
            self.reportar(nodo, f"'{nodo.contenido}' es un ritual: para usarlo hay que invocarlo con ⟅⟆")
            return self.decorar(nodo, tipos.DESCONOCIDO)
        return self.decorar(nodo, simbolo.tipo or tipos.DESCONOCIDO)

    def visitar_LlamadaRitual(self, nodo):
        """
        El tipo de una llamada es el tipo de retorno del ritual. También
        valida que cada argumento tenga el tipo del parámetro correspondiente.
        La cantidad de argumentos la valida la tabla de símbolos.
        """
        argumentos = nodo.hijos[0].hijos if nodo.hijos else []
        tipos_argumentos = [self.inferir_argumento(arg) for arg in argumentos]

        simbolo = self.tabla.buscar(nodo.contenido)
        if simbolo is not None and simbolo.categoria == RITUAL:
            for arg, tipo_param, tipo_arg in zip(argumentos, simbolo.parametros, tipos_argumentos):
                if not tipos.es_compatible(tipo_param, tipo_arg):
                    self.reportar(
                        arg,
                        f"El ritual '{nodo.contenido}' espera un argumento de tipo "
                        f"{tipo_param}, pero recibió {tipo_arg}",
                    )
            return self.decorar(nodo, simbolo.tipo_retorno or tipos.CENIZA)

        if simbolo is not None:
            self.reportar(nodo, f"'{nodo.contenido}' es una variable de tipo {simbolo.tipo}, no un ritual")
            return self.decorar(nodo, tipos.DESCONOCIDO)

        if nodo.contenido in RITUALES_ESTANDAR:
            return self.decorar(nodo, self.tipo_ritual_estandar(nodo.contenido, argumentos, tipos_argumentos))

        return self.decorar(nodo, tipos.DESCONOCIDO)

    def inferir_argumento(self, nodo):
        """
        Un argumento puede ser una expresión o un tipo (revivir⟅calavera⟆).
        En el segundo caso el "tipo" del argumento es el tipo nombrado.
        """
        if nodo.tipo == "Tipo":
            return nodo.contenido
        return self.inferir(nodo)

    @staticmethod
    def tipo_ritual_estandar(nombre, argumentos, tipos_argumentos):
        """Tipo de retorno de un ritual del ambiente estándar."""
        if nombre == "revivir":
            # revivir⟅calavera⟆ lee un valor y lo convierte al tipo pedido
            if argumentos and argumentos[0].tipo == "Tipo":
                return argumentos[0].contenido
            return tipos.CANTICO
        if nombre == "extraer":
            # extraer⟅fosa, posicion⟆ devuelve un elemento de la fosa
            if tipos_argumentos:
                return tipos.tipo_elemento(tipos_argumentos[0])
            return tipos.DESCONOCIDO
        return RITUALES_ESTANDAR[nombre]

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------

    def visitar_OperacionAritmetica(self, nodo):
        izquierdo, derecho = self.inferir_operandos(nodo)
        resultado = tipos.tipo_aritmetico(nodo.contenido, izquierdo, derecho)
        if resultado is None:
            self.reportar_operacion_invalida(nodo, izquierdo, derecho)
            return self.decorar(nodo, tipos.DESCONOCIDO)
        return self.decorar(nodo, resultado)

    def visitar_Comparacion(self, nodo):
        izquierdo, derecho = self.inferir_operandos(nodo)
        resultado = tipos.tipo_comparacion(nodo.contenido, izquierdo, derecho)
        if resultado is None:
            self.reportar_operacion_invalida(nodo, izquierdo, derecho)
        # Aunque sea inválida, una comparación siempre produce un latido
        return self.decorar(nodo, tipos.LATIDO)

    def visitar_OperacionLogica(self, nodo):
        izquierdo, derecho = self.inferir_operandos(nodo)
        resultado = tipos.tipo_logico(izquierdo, derecho)
        if resultado is None:
            self.reportar_operacion_invalida(nodo, izquierdo, derecho)
        return self.decorar(nodo, tipos.LATIDO)

    def inferir_operandos(self, nodo):
        """Infiere el tipo del operando izquierdo y del derecho."""
        izquierdo = self.inferir(nodo.hijos[0]) if len(nodo.hijos) > 0 else tipos.DESCONOCIDO
        derecho = self.inferir(nodo.hijos[1]) if len(nodo.hijos) > 1 else tipos.DESCONOCIDO
        return izquierdo, derecho

    def reportar_operacion_invalida(self, nodo, izquierdo, derecho):
        operador = DESCRIPCION_OPERADOR.get(nodo.contenido, f"'{nodo.contenido}'")
        self.reportar(nodo, f"No se puede aplicar {operador} entre {izquierdo} y {derecho}")

    # ------------------------------------------------------------------
    # Validaciones de instrucciones (las llama el verificador principal)
    # ------------------------------------------------------------------

    def verificar_declaracion(self, nodo):
        """
        Valida que el valor inicial sea compatible con el tipo declarado.
        Ejemplo de error: calavera x <- "hola" ☩

        Decora el nodo Declaracion con el tipo declarado.

        Retorna:
            str: Tipo declarado de la variable.
        """
        tipo_declarado = nodo.hijos[0].contenido if nodo.hijos else tipos.DESCONOCIDO
        if len(nodo.hijos) > 1:
            tipo_valor = self.inferir(nodo.hijos[1])
            if not tipos.es_compatible(tipo_declarado, tipo_valor):
                self.reportar(
                    nodo.hijos[1],
                    f"No se puede inicializar '{nodo.contenido}' de tipo {tipo_declarado} "
                    f"con un valor de tipo {tipo_valor}",
                )
        return self.decorar(nodo, tipo_declarado)

    def verificar_asignacion(self, nodo):
        """
        Valida que el valor asignado sea compatible con el tipo de la variable.
        Ejemplo de error: x <- "hola" ☩   (con x de tipo calavera)

        Decora el nodo Asignacion con el tipo de la variable destino.

        Retorna:
            str: Tipo de la variable, o DESCONOCIDO si no está declarada.
        """
        tipo_valor = self.inferir(nodo.hijos[0]) if nodo.hijos else tipos.DESCONOCIDO
        simbolo = self.tabla.buscar(nodo.contenido)

        if simbolo is None:
            return self.decorar(nodo, tipos.DESCONOCIDO)
        if simbolo.categoria == RITUAL:
            self.reportar(nodo, f"No se puede asignar un valor a '{nodo.contenido}' porque es un ritual")
            return self.decorar(nodo, tipos.DESCONOCIDO)

        tipo_destino = simbolo.tipo or tipos.DESCONOCIDO
        if not tipos.es_compatible(tipo_destino, tipo_valor):
            self.reportar(
                nodo,
                f"No se puede asignar un valor de tipo {tipo_valor} a "
                f"'{nodo.contenido}', que es de tipo {tipo_destino}",
            )
        return self.decorar(nodo, tipo_destino)

    def verificar_sacrificio(self, nodo, tipo_retorno):
        """
        Valida que el valor de 'sacrificar' coincida con el tipo de retorno
        declarado del ritual (⚯ tipo).

        Parámetros:
            nodo: Nodo Sacrificio.
            tipo_retorno (str | None): Tipo declarado del ritual, o None si
                el ritual no declara tipo de retorno.

        Retorna:
            str: Tipo del valor sacrificado (CENIZA si no lleva valor).
        """
        tiene_valor = len(nodo.hijos) > 0
        tipo_valor = self.inferir(nodo.hijos[0]) if tiene_valor else tipos.CENIZA

        if tipo_retorno is None and tiene_valor and tipo_valor != tipos.CENIZA:
            self.reportar(
                nodo,
                f"El ritual no declara tipo de retorno (⚯) pero sacrifica un valor de tipo {tipo_valor}",
            )
        elif tipo_retorno is not None and not tiene_valor:
            self.reportar(nodo, f"El ritual debe sacrificar un valor de tipo {tipo_retorno}")
        elif tipo_retorno is not None and not tipos.es_compatible(tipo_retorno, tipo_valor):
            self.reportar(
                nodo,
                f"El ritual debe sacrificar un valor de tipo {tipo_retorno}, pero sacrifica {tipo_valor}",
            )

        return self.decorar(nodo, tipo_valor)

    def exigir_latido(self, nodo_condicion, contexto):
        """
        Valida que una condición (mana, sin mana, persistir) sea de tipo latido.

        Parámetros:
            nodo_condicion: Expresión de la condición.
            contexto (str): Nombre de la estructura, para el mensaje de error.

        Retorna:
            str: Tipo inferido de la condición.
        """
        tipo = self.inferir(nodo_condicion)
        if tipo not in (tipos.LATIDO, tipos.DESCONOCIDO):
            self.reportar(nodo_condicion, f"La condición de '{contexto}' debe ser latido, pero es {tipo}")
        return tipo
