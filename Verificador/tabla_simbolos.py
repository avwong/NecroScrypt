"""
Tabla de símbolos de NecroScrypt.

Implementa el contrato definido en Comun/simbolos.py: guarda las variables,
los parámetros y los rituales declarados en una pila de ámbitos, y ofrece
tabla.buscar(nombre) a la inferencia de tipos y al generador de código.

Ámbitos:
    - El ámbito global (siempre existe).
    - El cuerpo de cada ritual (incluye a sus parámetros).
    - Cada bloque ✦ ✧ interno.

Regla de redeclaración:
    El Python generado solo crea variables nuevas dentro de funciones, por lo
    que un nombre no puede declararse dos veces dentro del mismo ritual (ni
    dos veces en el nivel global), aunque la segunda declaración esté en un
    bloque más interno. Un ritual sí puede declarar un nombre que también
    existe en el ámbito global: lo oculta dentro de su cuerpo.

Cada vez que la tabla cambia (se entra a un ámbito, se declara un símbolo o
se sale de un ámbito) se imprime su contenido para poder seguir el recorrido.
"""

from Comun import tipos
from Comun.errores import ErrorSemantico
from Comun.rituales import INCORPORADOS
from Comun.simbolos import RITUAL, VARIABLE, Simbolo

AMBITO_GLOBAL = "global"

ENCABEZADO_TABLA = ("Nombre", "Categoría", "Tipo", "Línea")


class Ambito:
    """
    Conjunto de símbolos declarados en una región del programa.

    Atributos:
        nombre (str): Nombre descriptivo, usado al imprimir la tabla.
        es_funcion (bool): True si es el ámbito global o el de un ritual,
            que es donde Python crea las variables locales.
        simbolos (dict): Símbolos del ámbito, en orden de declaración.
    """

    def __init__(self, nombre, es_funcion=False):
        self.nombre = nombre
        self.es_funcion = es_funcion
        self.simbolos = {}


class TablaSimbolos:
    """
    Pila de ámbitos con los símbolos declarados en el programa.

    Parámetros:
        errores (list, opcional): Lista donde se agregan los ErrorSemantico.
        imprimir (bool): Si es True, imprime la tabla cada vez que cambia.
        salida (callable): Función usada para imprimir (por defecto print).
    """

    def __init__(self, errores=None, imprimir=True, salida=print):
        self.errores = errores if errores is not None else []
        self.imprimir_cambios = imprimir
        self.salida = salida
        self.ambitos = [Ambito(AMBITO_GLOBAL, es_funcion=True)]

    @property
    def ambito_actual(self):
        """Retorna el ámbito más interno."""
        return self.ambitos[-1]

    # ------------------------------------------------------------------
    # Ámbitos
    # ------------------------------------------------------------------

    def entrar_ambito(self, nombre, es_funcion=False):
        """
        Abre un nuevo ámbito dentro del actual.

        Parámetros:
            nombre (str): Nombre descriptivo del ámbito.
            es_funcion (bool): True si es el cuerpo de un ritual.
        """
        self.ambitos.append(Ambito(nombre, es_funcion))
        self.registrar_cambio(f"Se entra al ámbito '{nombre}'")

    def salir_ambito(self):
        """
        Cierra el ámbito actual y descarta sus símbolos. El ámbito global
        nunca se cierra.

        Retorna:
            Ambito: El ámbito cerrado, o None si solo quedaba el global.
        """
        if len(self.ambitos) == 1:
            return None
        ambito = self.ambitos.pop()
        self.registrar_cambio(f"Se sale del ámbito '{ambito.nombre}'")
        return ambito

    # ------------------------------------------------------------------
    # Declaraciones
    # ------------------------------------------------------------------

    def declarar(self, nodo, tipo, categoria=VARIABLE):
        """
        Declara una variable o un parámetro en el ámbito actual. El nombre
        se toma de nodo.contenido.

        Parámetros:
            nodo (NodoASA): Nodo donde se declara (Declaracion, Parametro...).
            tipo (str): Tipo declarado ('calavera', 'fosa cantico', ...).
            categoria (str): VARIABLE o PARAMETRO.

        Retorna:
            Simbolo: El símbolo creado, o None si era una redeclaración.
        """
        simbolo = Simbolo(nodo.contenido, tipo, categoria, nodo=nodo)
        return self.insertar(nodo, simbolo)

    def declarar_ritual(self, nodo, parametros, tipo_retorno):
        """
        Declara un ritual en el ámbito actual con su firma.

        Parámetros:
            nodo (NodoASA): Nodo Ritual.
            parametros (list): Tipos de los parámetros, en orden.
            tipo_retorno (str): Tipo de retorno, o None si no devuelve nada.

        Retorna:
            Simbolo: El símbolo creado, o None si era una redeclaración.
        """
        simbolo = Simbolo(nodo.contenido, tipo_retorno, RITUAL, list(parametros), tipo_retorno, nodo)
        return self.insertar(nodo, simbolo)

    def insertar(self, nodo, simbolo):
        """
        Agrega un símbolo al ámbito actual validando que no esté repetido.

        Retorna:
            Simbolo: El símbolo agregado, o None si se reportó un error.
        """
        if simbolo.nombre in INCORPORADOS:
            self.reportar(nodo, f"'{simbolo.nombre}' es un ritual incorporado y no se puede redeclarar")
            return None

        anterior = self.buscar_conflicto(simbolo.nombre)
        if anterior is not None:
            linea = anterior.nodo.posicion()[0]
            self.reportar(
                nodo,
                f"'{simbolo.nombre}' ya fue declarado como {anterior.categoria} en la línea {linea}",
            )
            return None

        self.ambito_actual.simbolos[simbolo.nombre] = simbolo
        self.registrar_cambio(f"Se declara '{simbolo.nombre}' ({simbolo.categoria})")
        return simbolo

    def buscar_conflicto(self, nombre):
        """
        Busca un nombre ya declarado dentro de la misma función de Python:
        desde el ámbito actual hacia afuera, hasta el global o el ritual.

        Retorna:
            Simbolo: El símbolo que choca con el nombre, o None.
        """
        for ambito in reversed(self.ambitos):
            if nombre in ambito.simbolos:
                return ambito.simbolos[nombre]
            if ambito.es_funcion:
                break
        return None

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def buscar(self, nombre):
        """
        Busca un símbolo desde el ámbito actual hacia el global y, por último,
        entre los rituales incorporados.

        Retorna:
            Simbolo: El símbolo encontrado, o None.
        """
        for ambito in reversed(self.ambitos):
            if nombre in ambito.simbolos:
                return ambito.simbolos[nombre]
        return INCORPORADOS.get(nombre)

    def es_global(self, simbolo):
        """
        Indica si un símbolo pertenece al ámbito global. El generador lo usa
        para escribir 'global x' cuando un ritual asigna una variable global.
        """
        return self.ambitos[0].simbolos.get(simbolo.nombre) is simbolo

    def resolver(self, nodo, es_llamada=False):
        """
        Busca el símbolo al que se refiere un nodo, lo deja guardado en
        nodo.simbolo_ref y reporta el error si no está declarado.

        Parámetros:
            nodo (NodoASA): Identificador, LlamadaRitual o Asignacion.
            es_llamada (bool): True si el nodo invoca un ritual.

        Retorna:
            Simbolo: El símbolo encontrado, o None si no está declarado.
        """
        simbolo = self.buscar(nodo.contenido)
        if simbolo is None:
            descripcion = "El ritual" if es_llamada else "La variable"
            articulo = "declarado" if es_llamada else "declarada"
            self.reportar(nodo, f"{descripcion} '{nodo.contenido}' no ha sido {articulo}")
        nodo.simbolo_ref = simbolo
        return simbolo

    def reportar(self, nodo, mensaje):
        """Registra un error semántico en la posición del nodo."""
        linea, columna = nodo.posicion()
        error = ErrorSemantico(linea, columna, mensaje)
        self.errores.append(error)
        return error

    # ------------------------------------------------------------------
    # Impresión
    # ------------------------------------------------------------------

    @staticmethod
    def describir_tipo(simbolo):
        """Texto de la columna Tipo: el tipo de una variable o la firma de un ritual."""
        if simbolo.categoria == RITUAL:
            parametros = ", ".join(simbolo.parametros)
            return f"({parametros}) -> {simbolo.tipo_retorno or tipos.CENIZA}"
        return simbolo.tipo or tipos.DESCONOCIDO

    def a_texto(self):
        """
        Genera el contenido actual de la tabla, un bloque por cada ámbito
        abierto, desde el global hasta el actual.
        """
        lineas = []
        for ambito in self.ambitos:
            lineas.append(f"  Ámbito '{ambito.nombre}':")
            if not ambito.simbolos:
                lineas.append("    (vacío)")
                continue

            filas = [ENCABEZADO_TABLA]
            for simbolo in ambito.simbolos.values():
                linea = simbolo.nodo.posicion()[0]
                filas.append((simbolo.nombre, simbolo.categoria, self.describir_tipo(simbolo), str(linea)))

            anchos = [max(len(fila[i]) for fila in filas) for i in range(len(ENCABEZADO_TABLA))]
            filas.insert(1, tuple("-" * ancho for ancho in anchos))
            for fila in filas:
                texto = "  ".join(celda.ljust(ancho) for celda, ancho in zip(fila, anchos))
                lineas.append("    " + texto.rstrip())
        return "\n".join(lineas)

    def imprimir(self):
        """Imprime el contenido actual de la tabla."""
        self.salida(self.a_texto())

    def registrar_cambio(self, descripcion):
        """Imprime qué cambió y cómo quedó la tabla (si la impresión está activa)."""
        if self.imprimir_cambios:
            self.salida(f"\n[Tabla de símbolos] {descripcion}")
            self.imprimir()
