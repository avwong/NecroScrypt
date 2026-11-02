"""
Definición de NodoASA para el Árbol de Sintaxis Abstracta (ASA) de NecroScrypt.

El ASA es una estructura de datos jerárquica (árbol) donde cada nodo representa
una construcción gramatical del programa (declaración, ritual, bucle, expresión, etc.).
"""


class NodoASA:
    """
    Representa un nodo individual dentro del Árbol de Sintaxis Abstracta (ASA).

    Cada nodo almacena:
    - tipo: Qué categoría gramatical representa (ejemplo: 'Ritual', 'Declaracion', 'Entero').
    - contenido: Valor textual o nombre (ejemplo: 'main', '20', 'suma').
    - atributos: Posición de origen en el código fuente (ejemplo: 'línea = 2, columna = 5').
    - hijos: Lista de nodos que dependen de este nodo en la jerarquía sintáctica.
    """

    def __init__(self, tipo, contenido="", atributos="", hijos=None):
        self.tipo = str(tipo)
        self.contenido = str(contenido)
        self.atributos = str(atributos)

        if hijos is not None:
            self.hijos = list(hijos)
        else:
            self.hijos = []

    @classmethod
    def desde_token(cls, tipo, token, contenido=None):
        """
        Crea un nuevo nodo ASA extrayendo automáticamente la línea y la columna
        del Token que le dio origen.
        """
        if contenido is None:
            texto_contenido = token.contenido
        else:
            texto_contenido = contenido

        atributos_posicion = f"línea = {token.linea}, columna = {token.columna}"
        return cls(tipo, texto_contenido, atributos_posicion)

    def agregar_hijo(self, nodo_hijo):
        """
        Añade un nodo hijo a la lista de subordinados.
        Si el nodo recibido es None, lo ignora de forma segura.
        """
        if nodo_hijo is not None:
            self.hijos.append(nodo_hijo)
        return nodo_hijo

    def __repr__(self):
        """
        Representación textual estándar de un nodo del ASA:
        <"Tipo", "Contenido", "Atributos">
        """
        return f'<"{self.tipo}", "{self.contenido}", "{self.atributos}">'

    def preorden(self, usar_sangria=True, nivel_profundidad=0):
        """
        Recorre el árbol en orden previo (preorden):
        1. Primero procesa el nodo actual (padre).
        2. Luego procesa recursivamente cada hijo de izquierda a derecha.

        Retorna una lista de cadenas, una línea por cada nodo.
        """
        # Calcular los espacios de sangría según la profundidad actual
        if usar_sangria:
            espacios = "  " * nivel_profundidad
        else:
            espacios = ""

        # Agregar el nodo actual con su sangría correspondiente
        lineas = [espacios + repr(self)]

        # Recorrer e incluir los subárboles de cada hijo
        for hijo in self.hijos:
            lineas_del_hijo = hijo.preorden(usar_sangria, nivel_profundidad + 1)
            lineas.extend(lineas_del_hijo)

        return lineas

    def a_texto(self, usar_sangria=True):
        """
        Genera la representación completa del árbol en texto multilínea,
        lista para comparar o mostrar en pantalla.
        """
        lineas = self.preorden(usar_sangria)
        return "\n".join(lineas)

    def imprimir(self, usar_sangria=True):
        """
        Imprime el árbol completo en la consola con sangría jerárquica.
        """
        print(self.a_texto(usar_sangria))
