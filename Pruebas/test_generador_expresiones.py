"""
Pruebas de la generación de código Python para expresiones y asignaciones.

Cada prueba decora el ASA con la inferencia de tipos, genera el código y,
cuando aplica, lo ejecuta con Python para comprobar el resultado.

Ejecutar desde la raíz del proyecto:
    python -m unittest discover -s Pruebas -t .
"""

import unittest

from Comun import tipos
from Generador.expresiones import GeneradorExpresiones
from Generador.nombres import nombre_python
from Pruebas.utilidades import TablaDePrueba, primera_instruccion
from Verificador.inferencia_tipos import InferenciaTipos


class GeneradorDePrueba(GeneradorExpresiones):
    """Traducción simple de llamadas; la real la implementa otra parte del generador."""

    def visitar_LlamadaRitual(self, nodo):
        argumentos = [self.visitar(arg) for arg in nodo.hijos[0].hijos]
        return f"{nombre_python(nodo.contenido)}({', '.join(argumentos)})"


def generar_asignacion(codigo, tabla=None):
    """Analiza 'x <- expresion ☩', la verifica y retorna el código Python."""
    tabla = tabla or TablaDePrueba().variable("x", tipos.DESCONOCIDO)
    nodo = primera_instruccion(codigo)
    inferencia = InferenciaTipos(tabla)
    inferencia.verificar_asignacion(nodo)
    assert not inferencia.errores, inferencia.errores
    return GeneradorDePrueba().visitar(nodo)


def evaluar(linea, **variables):
    """Ejecuta una línea 'x = ...' y retorna el valor final de x."""
    entorno = dict(variables)
    exec(linea, {}, entorno)
    return entorno["x"]


class PruebasLiterales(unittest.TestCase):

    def test_literales(self):
        casos = {
            "x <- 20 ☩": "x = 20",
            "x <- 007 ☩": "x = 7",
            "x <- 3.14 ☩": "x = 3.14",
            'x <- "Pepe el mago" ☩': "x = 'Pepe el mago'",
            "x <- vivo ☩": "x = True",
            "x <- muerto ☩": "x = False",
            "x <- ceniza ☩": "x = None",
        }
        for codigo, esperado in casos.items():
            with self.subTest(codigo=codigo):
                self.assertEqual(generar_asignacion(codigo), esperado)

    def test_fosa(self):
        nodo = primera_instruccion("fosa esencia a <- ☾1, 2.5☽ ☩")
        InferenciaTipos(TablaDePrueba()).verificar_declaracion(nodo)
        self.assertEqual(GeneradorDePrueba().visitar(nodo.hijos[1]), "[float(1), 2.5]")


class PruebasOperaciones(unittest.TestCase):

    def test_operadores_aritmeticos(self):
        casos = {
            "x <- 7 ensamblar 2 ☩": ("x = 7 + 2", 9),
            "x <- 7 mutilar 2 ☩": ("x = 7 - 2", 5),
            "x <- 7 infestar 2 ☩": ("x = 7 * 2", 14),
            "x <- 7 restos 2 ☩": ("x = 7 % 2", 1),
            "x <- 7 desmembrar 2 ☩": ("x = 7 // 2", 3),
            "x <- 7.0 desmembrar 2 ☩": ("x = 7.0 / 2", 3.5),
        }
        for codigo, (esperado, valor) in casos.items():
            with self.subTest(codigo=codigo):
                linea = generar_asignacion(codigo)
                self.assertEqual(linea, esperado)
                self.assertEqual(evaluar(linea), valor)

    def test_respeta_agrupacion_del_asa(self):
        linea = generar_asignacion("x <- ⟅1 ensamblar 2⟆ infestar 3 ☩")
        self.assertEqual(linea, "x = (1 + 2) * 3")
        self.assertEqual(evaluar(linea), 9)

        linea = generar_asignacion("x <- 10 mutilar ⟅4 mutilar 1⟆ ☩")
        self.assertEqual(evaluar(linea), 7)

    def test_precedencia_del_lenguaje(self):
        linea = generar_asignacion("x <- 1 ensamblar 2 infestar 3 ☩")
        self.assertEqual(linea, "x = 1 + (2 * 3)")
        self.assertEqual(evaluar(linea), 7)

    def test_concatenacion(self):
        linea = generar_asignacion('x <- "hola " ensamblar "mundo" ☩')
        self.assertEqual(evaluar(linea), "hola mundo")

    def test_comparaciones_y_logicas(self):
        linea = generar_asignacion("x <- 1 < 2 y 3 != 3 o vivo ☩")
        self.assertEqual(linea, "x = ((1 < 2) and (3 != 3)) or True")
        self.assertTrue(evaluar(linea))


class PruebasIdentificadoresYConversiones(unittest.TestCase):

    def test_identificadores_protegidos(self):
        self.assertEqual(nombre_python("vida"), "vida")
        self.assertEqual(nombre_python("class"), "class_")
        self.assertEqual(nombre_python("print"), "print_")

    def test_asignacion_con_variables(self):
        tabla = TablaDePrueba().variable("x", tipos.CALAVERA).variable("vida", tipos.CALAVERA)
        linea = generar_asignacion("x <- vida infestar 2 ☩", tabla)
        self.assertEqual(linea, "x = vida * 2")
        self.assertEqual(evaluar(linea, vida=21), 42)

    def test_calavera_en_esencia_se_convierte(self):
        tabla = TablaDePrueba().variable("x", tipos.ESENCIA)
        linea = generar_asignacion("x <- 5 ☩", tabla)
        self.assertEqual(linea, "x = float(5)")
        self.assertIsInstance(evaluar(linea), float)

    def test_conversion_a_cantico(self):
        generador = GeneradorDePrueba()
        inferencia = InferenciaTipos(TablaDePrueba())
        casos = {
            "x <- 20 ☩": ("str(20)", "20"),
            "x <- vivo ☩": ('("vivo" if True else "muerto")', "vivo"),
            "x <- ceniza ☩": ('"ceniza"', "ceniza"),
        }
        for codigo, (esperado, valor) in casos.items():
            with self.subTest(codigo=codigo):
                expresion = primera_instruccion(codigo).hijos[0]
                inferencia.inferir(expresion)
                generado = generador.convertir_a(expresion, tipos.CANTICO)
                self.assertEqual(generado, esperado)
                self.assertEqual(eval(generado), valor)

    def test_llamada_dentro_de_expresion(self):
        tabla = (
            TablaDePrueba()
            .variable("x", tipos.CALAVERA)
            .ritual("fibonacci", [tipos.CALAVERA], tipos.CALAVERA)
        )
        linea = generar_asignacion("x <- fibonacci⟅10⟆ ensamblar 1 ☩", tabla)
        self.assertEqual(linea, "x = fibonacci(10) + 1")

    def test_nodo_sin_traduccion_avisa(self):
        nodo = primera_instruccion("mana⟅vivo⟆ ✦ ✧")
        with self.assertRaises(NotImplementedError):
            GeneradorExpresiones().visitar(nodo)


if __name__ == "__main__":
    unittest.main()
