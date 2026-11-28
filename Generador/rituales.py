"""
Generación de código Python para los rituales de NecroScrypt: definición,
invocación, retorno y paso de argumentos.

GeneradorRituales es un visitante pensado para combinarse por herencia con
GeneradorExpresiones (necesita convertir_a y nombre_python) y con
GeneradorBase, en Generador/generador.py.

    ritual suma⟅calavera a, calavera b⟆ ⚯ calavera ✦    def suma(a, b):
        sacrificar a ensamblar b ☩                    ->        return a + b
    ✧

Requiere que el verificador haya decorado el ASA (simbolo_ref y tipo_inferido).
"""

from Comun.rituales import es_incorporado, separar_ritual
from Comun.simbolos import RITUAL
from Generador.expresiones import nombre_python


class GeneradorRituales:
    """Traduce definiciones, llamadas y retornos de rituales a Python 3.8+."""

    # ------------------------------------------------------------------
    # Definición
    # ------------------------------------------------------------------

    def visitar_Ritual(self, nodo):
        """
        Escribe 'def nombre(parametros):' y su cuerpo. Si el ritual asigna una
        variable global se agrega 'global x' al inicio, porque en Python una
        asignación dentro de una función crearía una variable local nueva.
        """
        parametros, tipo_retorno, bloque = separar_ritual(nodo)
        nombres = ", ".join(nombre_python(parametro.contenido) for parametro in parametros)
        self.emitir(f"def {nombre_python(nodo.contenido)}({nombres}):")

        instrucciones = bloque.hijos if bloque is not None else []
        globales = self.globales_asignadas(bloque)
        preambulo = [f"global {', '.join(globales)}"] if globales else []

        self.tipos_retorno.append(tipo_retorno)
        self.generar_cuerpo(instrucciones, preambulo)
        self.tipos_retorno.pop()

        self.emitir()
        self.emitir()

    def globales_asignadas(self, raiz):
        """
        Busca las variables globales que se asignan dentro de un ritual.

        Parámetros:
            raiz (NodoASA): Bloque del ritual, o None.

        Retorna:
            list: Nombres Python de las variables globales asignadas, sin repetir.
        """
        nombres = []
        if raiz is None or self.tabla is None:
            return nombres

        pendientes = [raiz]
        while pendientes:
            nodo = pendientes.pop(0)
            simbolo = nodo.simbolo_ref
            if nodo.tipo == "Asignacion" and simbolo is not None and self.tabla.es_global(simbolo):
                nombre = nombre_python(nodo.contenido)
                if nombre not in nombres:
                    nombres.append(nombre)
            pendientes = list(nodo.hijos) + pendientes
        return nombres

    # ------------------------------------------------------------------
    # Retorno
    # ------------------------------------------------------------------

    def visitar_Sacrificio(self, nodo):
        """
        sacrificar valor ☩   ->   return valor

        Una calavera sacrificada en un ritual que devuelve esencia se
        convierte con float().
        """
        if not nodo.hijos:
            self.emitir("return")
            return
        tipo_retorno = self.tipos_retorno[-1] if self.tipos_retorno else None
        self.emitir(f"return {self.convertir_a(nodo.hijos[0], tipo_retorno)}")

    # ------------------------------------------------------------------
    # Invocación
    # ------------------------------------------------------------------

    def visitar_LlamadaRitual(self, nodo):
        """
        nombre⟅a, b⟆   ->   nombre(a, b)

        Cada argumento se convierte al tipo del parámetro correspondiente
        (una calavera pasada a un parámetro esencia lleva float()).
        """
        argumentos = nodo.hijos[0].hijos if nodo.hijos else []
        simbolo = nodo.simbolo_ref

        if es_incorporado(simbolo):
            return self.generar_incorporada(nodo, argumentos)

        tipos_parametros = []
        if simbolo is not None and simbolo.categoria == RITUAL:
            tipos_parametros = simbolo.parametros

        codigos = []
        for posicion, argumento in enumerate(argumentos):
            destino = tipos_parametros[posicion] if posicion < len(tipos_parametros) else None
            codigos.append(self.convertir_a(argumento, destino))
        return f"{nombre_python(nodo.contenido)}({', '.join(codigos)})"

    def generar_incorporada(self, nodo, argumentos):
        """
        Traduce una llamada a un ritual incorporado. Por ahora 'invocar' se
        traduce a print; 'revivir' todavía no tiene traducción.

        Retorna:
            str: Código Python de la llamada.
        """
        if nodo.contenido == "invocar":
            codigos = [self.visitar(argumento) for argumento in argumentos]
            return f"print({', '.join(codigos)})"
        raise NotImplementedError(
            f"El generador todavía no traduce el ritual incorporado '{nodo.contenido}'"
        )
