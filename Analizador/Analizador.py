""" la clase del analizador

El objetivo es que retorne un ASA Arbol Syntax Abstracta
Ya listo para el verificador

DISEÑO DEL ASA:

Formato de impresion (un nodo por linea):
    <"Tipo", "Contenido", "Atributos">

Convenciones:
    - Atributos: "línea = L, columna = C", tomado del token que origino el
      nodo (igual que el explorador). Los nodos agrupadores sin token usan ""
    - No aparecen en el arbol: ☩ ✦ ✧ ⟅ ⟆ ☾ ☽ <- , ⚯ ni las palabras clave que
      ya definen el tipo de nodo
    - Los comentarios ~~...~~ se omiten del arbol (el parser los acepta y los
      salta)
    - TipoRetorno solo existe si el ritual tiene ⚯; si no, no hay nodo.
    - Tipo es un nodo hijo (hoja), nunca un atributo del padre.
    - Los operadores van en el contenido del nodo binario. La precedencia
      queda resuelta por la forma del arbol:
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

class Analizador():
	pass
