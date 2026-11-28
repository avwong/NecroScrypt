"""
Generación de código Python para las estructuras de control de NecroScrypt
(condicionales, bucles y bloques).

GeneradorControl se combina por herencia con el resto del generador en
Generador/generador.py. Requiere que el ASA esté decorado (tipo_inferido)
y que existan en la clase combinada:

    emitir(linea)              # de GeneradorBase
    generar_bloque(bloque)     # de GeneradorBase (sube sangría un nivel)
    visitar(expresion)         # de GeneradorExpresiones
    nombre_python(nombre)      # de Generador/expresiones.py

Formas del ASA producidas por el Analizador:

    Condicional        -> [Mana, SinMana*, Sin?]
    Mana / SinMana     -> [condicion, Bloque]
    Sin                -> [Bloque]
    BuclePersistir     -> [condicion, Bloque]
    BucleConvocar      -> [Tipo, coleccion, Bloque]
"""

from Generador.expresiones import nombre_python


class GeneradorControl:
    """Traduce condicionales, bucles y bloques del ASA a Python 3.8+."""

    # ------------------------------------------------------------------
    # Condicionales (mana / sin mana / sin)
    # ------------------------------------------------------------------

    def visitar_Condicional(self, nodo):
        """
        Condicional -> [Mana, SinMana*, Sin?]

        Se emiten como una cadena if / elif / else en el mismo nivel de
        sangría. Si solo hay un 'Sin' sin 'Mana' previo, se emite un bloque
        suelto (raro pero válido).
        """
        for rama in nodo.hijos:
            if rama.tipo == "Mana":
                self._emitir_rama(rama, "if")
            elif rama.tipo == "SinMana":
                self._emitir_rama(rama, "elif")
            elif rama.tipo == "Sin":
                self.emitir("else:")
                self.generar_bloque(rama.hijos[0])
        self.emitir()

    def _emitir_rama(self, rama, palabra):
        """Escribe 'if|elif <cond>:' y el cuerpo de una rama Mana/SinMana."""
        condicion = self.visitar(rama.hijos[0])
        self.emitir(f"{palabra} {condicion}:")
        self.generar_bloque(rama.hijos[1])

    # ------------------------------------------------------------------
    # Bucles
    # ------------------------------------------------------------------

    def visitar_BuclePersistir(self, nodo):
        """
        persistir ⟅cond⟆ Bloque   ->   while cond:
                                           <cuerpo>
        """
        condicion = self.visitar(nodo.hijos[0])
        self.emitir(f"while {condicion}:")
        self.generar_bloque(nodo.hijos[1])
        self.emitir()

    def visitar_BucleConvocar(self, nodo):
        """
        convocar Tipo var en coleccion Bloque   ->   for var in coleccion:
                                                         <cuerpo>
        """
        nombre = nombre_python(nodo.contenido)
        coleccion = self.visitar(nodo.hijos[1])
        self.emitir(f"for {nombre} in {coleccion}:")
        self.generar_bloque(nodo.hijos[2])
        self.emitir()