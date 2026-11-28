"""
Base del generador de código Python de NecroScrypt.

Acumula las líneas de código que producen los visitantes, lleva el nivel de
sangría y ensambla el texto final. Las demás partes del generador
(expresiones, declaraciones, rituales, estructuras de control) se combinan
con esta clase por herencia múltiple en Generador/generador.py.

Convención para los visitantes del generador:

    - Los visitantes de expresiones retornan un str con el código Python.
    - Los visitantes de instrucciones simples (declaración, asignación,
      llamada) también retornan un str: generar_instruccion lo escribe con
      la sangría actual.
    - Los visitantes de instrucciones compuestas (rituales, if, while)
      escriben sus propias líneas con self.emitir y retornan None. El cuerpo
      se escribe con generar_cuerpo, que sube la sangría un nivel.
"""

from contextlib import contextmanager

from Comun.visitante import Visitante

ENCABEZADO = "# Código generado por el transpilador de NecroScrypt. No editar a mano."


class GeneradorBase(Visitante):
    """
    Maneja la salida del generador: líneas, sangría y ensamblado.

    Parámetros:
        tabla (TablaSimbolos, opcional): Tabla del verificador. Permite saber
            qué variables son globales.
    """

    SANGRIA = "    "

    def __init__(self, tabla=None):
        self.tabla = tabla
        self.lineas = []
        self.nivel = 0
        # Tipo de retorno de cada ritual que se está generando (None si no declara)
        self.tipos_retorno = []

    # ------------------------------------------------------------------
    # Salida
    # ------------------------------------------------------------------

    def emitir(self, codigo=""):
        """Escribe una línea con la sangría actual (una línea vacía no lleva sangría)."""
        if codigo:
            self.lineas.append(self.SANGRIA * self.nivel + codigo)
        else:
            self.lineas.append("")

    @contextmanager
    def indentar(self):
        """Sube la sangría un nivel mientras dure el bloque with."""
        self.nivel += 1
        try:
            yield
        finally:
            self.nivel -= 1

    def generar_instruccion(self, nodo):
        """
        Visita una instrucción y escribe el código que retorne, si retorna uno.
        Las instrucciones compuestas escriben sus propias líneas y retornan None.
        """
        codigo = self.visitar(nodo)
        if isinstance(codigo, str):
            self.emitir(codigo)

    def generar_cuerpo(self, instrucciones, preambulo=()):
        """
        Escribe una lista de instrucciones un nivel más adentro. Si no se
        escribe nada, agrega 'pass' para que el Python generado sea válido.

        Parámetros:
            instrucciones (list): Nodos de las instrucciones del cuerpo.
            preambulo (iterable): Líneas de código que van antes del cuerpo
                (por ejemplo, declaraciones 'global').
        """
        with self.indentar():
            inicio = len(self.lineas)
            for linea in preambulo:
                self.emitir(linea)
            for nodo in instrucciones:
                self.generar_instruccion(nodo)
            if len(self.lineas) == inicio:
                self.emitir("pass")

    def generar_bloque(self, bloque):
        """Escribe las instrucciones de un nodo Bloque como cuerpo sangrado."""
        self.generar_cuerpo(bloque.hijos)

    # ------------------------------------------------------------------
    # Programa
    # ------------------------------------------------------------------

    def visitar_Programa(self, nodo):
        """
        Escribe primero todos los rituales y después las instrucciones sueltas,
        de modo que una instrucción global pueda invocar un ritual aunque esté
        escrito más abajo en el código fuente. Si existe un ritual 'main' sin
        parámetros, se invoca al final.
        """
        rituales = [hijo for hijo in nodo.hijos if hijo.tipo == "Ritual"]
        instrucciones = [hijo for hijo in nodo.hijos if hijo.tipo != "Ritual"]

        for ritual in rituales:
            self.visitar(ritual)
        for instruccion in instrucciones:
            self.generar_instruccion(instruccion)

        if any(self.es_main_sin_parametros(ritual) for ritual in rituales):
            self.emitir("main()")

    @staticmethod
    def es_main_sin_parametros(ritual):
        """Indica si un nodo Ritual es 'main' y no recibe parámetros."""
        if ritual.contenido != "main":
            return False
        return all(len(hijo.hijos) == 0 for hijo in ritual.hijos if hijo.tipo == "Parametros")

    # ------------------------------------------------------------------
    # Ensamblado
    # ------------------------------------------------------------------

    def ensamblar(self):
        """
        Une las líneas generadas en el texto final del archivo .py.

        Retorna:
            str: Código Python con encabezado y un salto de línea final.
        """
        cuerpo = "\n".join(self.lineas).strip("\n")
        return f"{ENCABEZADO}\n\n{cuerpo}\n"

    def generar(self, asa):
        """
        Genera el código Python completo de un ASA ya decorado por el verificador.

        Parámetros:
            asa (NodoASA): Nodo raíz 'Programa'.

        Retorna:
            str: Código Python listo para escribir en un archivo.
        """
        self.lineas = []
        self.nivel = 0
        self.visitar(asa)
        return self.ensamblar()
