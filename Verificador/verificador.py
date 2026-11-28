"""
Verificador (checker) de NecroScrypt.

Recorre el ASA de forma descendente (Top-Down) con el patrón Visitante, lleva
la tabla de símbolos y decora el árbol:

    - nodo.simbolo_ref   referencia directa a la declaración del nombre usado
    - nodo.tipo_inferido tipo de cada expresión (lo calcula InferenciaTipos)

Reparto de trabajo entre las clases:

    Verificador       recorre instrucciones y administra los ámbitos
    ResolutorNombres  busca cada nombre usado en una expresión
    InferenciaTipos   calcula y valida los tipos de las expresiones
    TablaSimbolos     guarda las declaraciones

Los nodos que no tienen método propio (condicionales, bucles persistir, etc.)
se recorren con visitar_generico: sus expresiones se verifican y sus bloques
abren un ámbito nuevo.
"""

from Comun.rituales import separar_ritual, tipo_de_parametro
from Comun.simbolos import PARAMETRO
from Comun.visitante import Visitante
from Verificador.inferencia_tipos import InferenciaTipos
from Verificador.resolutor_nombres import ResolutorNombres
from Verificador.tabla_simbolos import TablaSimbolos
from Comun import tipos

# Tipos de nodo que representan expresiones (producen un valor)
EXPRESIONES = (
    "Entero",
    "Decimal",
    "Cadena",
    "Booleano",
    "Ceniza",
    "Lista",
    "Identificador",
    "LlamadaRitual",
    "OperacionAritmetica",
    "Comparacion",
    "OperacionLogica",
)


class Verificador(Visitante):
    """
    Verifica nombres y tipos del ASA y lo decora.

    Parámetros:
        imprimir_tabla (bool): Si es True, imprime la tabla de símbolos cada
            vez que cambia.

    Atributos:
        errores (list): ErrorSemantico encontrados durante el recorrido.
        tabla (TablaSimbolos): Tabla de símbolos del programa.
    """

    def __init__(self, imprimir_tabla=True):
        self.errores = []
        self.tabla = TablaSimbolos(self.errores, imprimir=imprimir_tabla)
        self.resolutor = ResolutorNombres(self.tabla)
        self.inferencia = InferenciaTipos(self.tabla, self.errores)
        # Tipo de retorno de cada ritual que se está verificando (None si no declara)
        self.tipos_retorno = []

    def verificar(self, asa):
        """
        Verifica y decora un ASA completo.

        Parámetros:
            asa (NodoASA): Nodo raíz 'Programa'.

        Retorna:
            list: Los errores semánticos encontrados (vacía si todo es correcto).
        """
        self.visitar(asa)
        self.errores.sort(key=lambda error: (error.linea, error.columna))
        return self.errores

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def verificar_expresion(self, nodo):
        """Resuelve los nombres de una expresión y luego infiere sus tipos."""
        self.resolutor.visitar(nodo)
        return self.inferencia.inferir(nodo)

    def visitar_hijo(self, nodo):
        """Visita un hijo como expresión si lo es, o como instrucción si no."""
        if nodo.tipo in EXPRESIONES:
            self.verificar_expresion(nodo)
        else:
            self.visitar(nodo)

    def visitar_instrucciones(self, bloque):
        """Visita las instrucciones de un bloque sin abrir un ámbito nuevo."""
        for instruccion in bloque.hijos:
            self.visitar_hijo(instruccion)

    def visitar_generico(self, nodo):
        """Recorre los hijos de un nodo sin comportamiento propio."""
        for hijo in nodo.hijos:
            self.visitar_hijo(hijo)

    # ------------------------------------------------------------------
    # Programa, rituales y bloques
    # ------------------------------------------------------------------

    def visitar_Programa(self, nodo):
        """
        Primero registra la firma de todos los rituales (así pueden invocarse
        entre sí sin importar el orden) y luego recorre el programa en orden.
        """
        for hijo in nodo.hijos:
            if hijo.tipo == "Ritual":
                self.declarar_ritual(hijo)
        for hijo in nodo.hijos:
            self.visitar_hijo(hijo)

    def declarar_ritual(self, nodo):
        """Registra el ritual en el ámbito global y lo deja en nodo.simbolo_ref."""
        parametros, tipo_retorno, _ = separar_ritual(nodo)
        tipos_parametros = [tipo_de_parametro(parametro) for parametro in parametros]
        nodo.simbolo_ref = self.tabla.declarar_ritual(nodo, tipos_parametros, tipo_retorno)

    def visitar_Ritual(self, nodo):
        """
        Abre el ámbito del ritual, declara sus parámetros y recorre el cuerpo.
        Los parámetros y las variables del cuerpo comparten el mismo ámbito.
        """
        parametros, tipo_retorno, bloque = separar_ritual(nodo)

        self.tabla.entrar_ambito(f"ritual {nodo.contenido}", es_funcion=True)
        for parametro in parametros:
            parametro.simbolo_ref = self.tabla.declarar(parametro, tipo_de_parametro(parametro), PARAMETRO)

        self.tipos_retorno.append(tipo_retorno)
        if bloque is not None:
            self.visitar_instrucciones(bloque)
        self.tipos_retorno.pop()

        self.tabla.salir_ambito()

    def visitar_Bloque(self, nodo):
        """Un bloque ✦ ✧ interno abre un ámbito propio."""
        self.tabla.entrar_ambito(f"bloque (nivel {len(self.tabla.ambitos)})")
        self.visitar_instrucciones(nodo)
        self.tabla.salir_ambito()

    # ------------------------------------------------------------------
    # Instrucciones que declaran, asignan o retornan
    # ------------------------------------------------------------------

    def visitar_Declaracion(self, nodo):
        """
        Verifica el valor inicial y después declara la variable, de modo que
        una variable no pueda usarse en su propia inicialización.
        """
        for valor in nodo.hijos[1:]:
            self.resolutor.visitar(valor)
        tipo_declarado = self.inferencia.verificar_declaracion(nodo)
        nodo.simbolo_ref = self.tabla.declarar(nodo, tipo_declarado)

    def visitar_Asignacion(self, nodo):
        """Resuelve la variable destino y valida el tipo del valor asignado."""
        for valor in nodo.hijos:
            self.resolutor.visitar(valor)
        self.tabla.resolver(nodo)
        self.inferencia.verificar_asignacion(nodo)

    def visitar_Sacrificio(self, nodo):
        """
        Resuelve el valor retornado, valida que 'sacrificar' aparezca dentro
        de un ritual y compara el tipo del valor con el tipo de retorno
        declarado del ritual (⚯).
        """
        for valor in nodo.hijos:
            self.resolutor.visitar(valor)

        if not self.tipos_retorno:
            # Fuera de cualquier ritual: no existe un tipo de retorno contra
            # el que comparar, y el mensaje de verificar_sacrificio (que asume
            # "ritual sin ⚯") sería engañoso. Igualmente inferimos los tipos
            # del valor para que el resto de fases no tropiece con nodos sin
            # decorar.
            for valor in nodo.hijos:
                self.inferencia.inferir(valor)
            self.tabla.reportar(
                nodo,
                "La sentencia 'sacrificar' solo puede usarse dentro de un ritual",
            )
            return

        self.inferencia.verificar_sacrificio(nodo, self.tipos_retorno[-1])
    def visitar_BucleConvocar(self, nodo):
        """
        convocar Tipo variable en coleccion ✦ ... ✧

        La colección se evalúa fuera del bucle; la variable del bucle y el
        cuerpo comparten un ámbito propio.
        """
        tipo = nodo.hijos[0]
        coleccion = nodo.hijos[1] if len(nodo.hijos) > 1 else None
        bloque = nodo.hijos[-1] if nodo.hijos[-1].tipo == "Bloque" else None

        if coleccion is not None and coleccion is not bloque:
            self.verificar_expresion(coleccion)

        self.tabla.entrar_ambito(f"convocar {nodo.contenido}")
        nodo.simbolo_ref = self.tabla.declarar(nodo, tipo.contenido)
        if bloque is not None:
            self.visitar_instrucciones(bloque)
        self.tabla.salir_ambito()
        
    # ------------------------------------------------------------------
    # Estructuras de control
    # ------------------------------------------------------------------

    def verificar_condicion(self, condicion, contexto):
        """
        Verifica que la condición de un 'mana', 'sin mana' o 'persistir'
        sea de tipo latido (booleana).

        Si el tipo es DESCONOCIDO (por ejemplo, porque la expresión contiene
        un nombre no declarado), no se reporta un error adicional para no
        generar cascadas de errores.
        """
        if condicion is None:
            return
        tipo = self.verificar_expresion(condicion)
        if tipo not in (tipos.LATIDO, tipos.DESCONOCIDO):
            self.tabla.reportar(
                condicion,
                f"La condición del '{contexto}' debe ser de tipo latido, "
                f"pero es de tipo {tipo}",
            )

    def visitar_rama_condicional(self, nodo, contexto):
        """Visita una rama condicional con la forma [condición, Bloque]."""
        condicion = nodo.hijos[0] if len(nodo.hijos) > 0 else None
        bloque = nodo.hijos[1] if len(nodo.hijos) > 1 else None
        self.verificar_condicion(condicion, contexto)
        if bloque is not None:
            self.visitar(bloque)

    def visitar_Mana(self, nodo):
        """Rama inicial 'mana ⟅cond⟆ ✦…✧' de un condicional."""
        self.visitar_rama_condicional(nodo, "mana")

    def visitar_SinMana(self, nodo):
        """Rama alternativa 'sin mana ⟅cond⟆ ✦…✧' de un condicional."""
        self.visitar_rama_condicional(nodo, "sin mana")

    def visitar_BuclePersistir(self, nodo):
        """Bucle 'persistir ⟅cond⟆ ✦…✧' (while)."""
        condicion = nodo.hijos[0] if len(nodo.hijos) > 0 else None
        bloque = nodo.hijos[1] if len(nodo.hijos) > 1 else None
        self.verificar_condicion(condicion, "persistir")
        if bloque is not None:
            self.visitar(bloque)
