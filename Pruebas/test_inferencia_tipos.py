"""
Pruebas del motor de inferencia de tipos.

Ejecutar desde la raíz del proyecto:
    python -m unittest discover -s Pruebas -t .
"""

import unittest

from Comun import tipos
from Pruebas.utilidades import TablaDePrueba, primera_instruccion
from Verificador.inferencia_tipos import InferenciaTipos


def inferir_asignacion(codigo, tabla=None):
    """Analiza 'x <- expresion ☩' y retorna (tipo de la expresión, errores)."""
    nodo = primera_instruccion(codigo)
    inferencia = InferenciaTipos(tabla or TablaDePrueba())
    tipo = inferencia.inferir(nodo.hijos[0])
    return tipo, inferencia.errores, nodo.hijos[0]


class PruebasLiterales(unittest.TestCase):

    def test_literales_primitivos(self):
        casos = {
            "x <- 20 ☩": tipos.CALAVERA,
            "x <- 3.14 ☩": tipos.ESENCIA,
            'x <- "hola" ☩': tipos.CANTICO,
            "x <- vivo ☩": tipos.LATIDO,
            "x <- muerto ☩": tipos.LATIDO,
            "x <- ceniza ☩": tipos.CENIZA,
        }
        for codigo, esperado in casos.items():
            with self.subTest(codigo=codigo):
                tipo, errores, _ = inferir_asignacion(codigo)
                self.assertEqual(tipo, esperado)
                self.assertEqual(errores, [])

    def test_fosas_literales(self):
        nodo = primera_instruccion("fosa calavera a <- ☾1, 2, 3☽ ☩")
        inferencia = InferenciaTipos(TablaDePrueba())
        self.assertEqual(inferencia.inferir(nodo.hijos[1]), "fosa calavera")

        nodo = primera_instruccion("fosa esencia a <- ☾1, 2.5☽ ☩")
        self.assertEqual(inferencia.inferir(nodo.hijos[1]), "fosa esencia")

        nodo = primera_instruccion("fosa calavera a <- ☾☽ ☩")
        self.assertEqual(inferencia.inferir(nodo.hijos[1]), tipos.FOSA_VACIA)
        self.assertEqual(inferencia.errores, [])

    def test_fosa_mezclada_es_error(self):
        nodo = primera_instruccion('fosa calavera a <- ☾1, "dos"☽ ☩')
        inferencia = InferenciaTipos(TablaDePrueba())
        inferencia.inferir(nodo.hijos[1])
        self.assertEqual(len(inferencia.errores), 1)
        self.assertIn("mismo tipo", inferencia.errores[0].mensaje)


class PruebasOperaciones(unittest.TestCase):

    def test_aritmetica_numerica(self):
        casos = {
            "x <- 1 ensamblar 2 ☩": tipos.CALAVERA,
            "x <- 1 ensamblar 2.0 ☩": tipos.ESENCIA,
            "x <- 7 desmembrar 2 ☩": tipos.CALAVERA,
            "x <- 7.0 desmembrar 2 ☩": tipos.ESENCIA,
            "x <- 7 restos 2 ☩": tipos.CALAVERA,
            "x <- 2 infestar ⟅3 mutilar 1.5⟆ ☩": tipos.ESENCIA,
        }
        for codigo, esperado in casos.items():
            with self.subTest(codigo=codigo):
                tipo, errores, _ = inferir_asignacion(codigo)
                self.assertEqual(tipo, esperado)
                self.assertEqual(errores, [])

    def test_concatenar_canticos(self):
        tipo, errores, _ = inferir_asignacion('x <- "hola " ensamblar "mundo" ☩')
        self.assertEqual(tipo, tipos.CANTICO)
        self.assertEqual(errores, [])

    def test_cantico_mas_calavera_es_error(self):
        tipo, errores, _ = inferir_asignacion('x <- "edad: " ensamblar 20 ☩')
        self.assertEqual(tipo, tipos.DESCONOCIDO)
        self.assertEqual(len(errores), 1)
        self.assertIn("cantico", errores[0].mensaje)
        self.assertIn("calavera", errores[0].mensaje)
        self.assertEqual(errores[0].linea, 1)

    def test_error_no_se_propaga_en_cascada(self):
        # Solo la suma interna es inválida; la externa no debe repetir el error
        _, errores, _ = inferir_asignacion('x <- ⟅"a" ensamblar 1⟆ ensamblar 2 ☩')
        self.assertEqual(len(errores), 1)

    def test_comparaciones(self):
        casos = {
            "x <- 1 < 2.5 ☩": [],
            'x <- "a" == "b" ☩': [],
            'x <- "a" < "b" ☩': [],
            "x <- vivo != muerto ☩": [],
        }
        for codigo, errores_esperados in casos.items():
            with self.subTest(codigo=codigo):
                tipo, errores, _ = inferir_asignacion(codigo)
                self.assertEqual(tipo, tipos.LATIDO)
                self.assertEqual(errores, errores_esperados)

    def test_comparacion_invalida(self):
        tipo, errores, _ = inferir_asignacion('x <- "a" < 3 ☩')
        self.assertEqual(tipo, tipos.LATIDO)
        self.assertEqual(len(errores), 1)

    def test_logicas(self):
        tipo, errores, _ = inferir_asignacion("x <- 1 < 2 y vivo ☩")
        self.assertEqual(tipo, tipos.LATIDO)
        self.assertEqual(errores, [])

        _, errores, _ = inferir_asignacion("x <- 1 o vivo ☩")
        self.assertEqual(len(errores), 1)

    def test_decora_todo_el_subarbol(self):
        _, _, expresion = inferir_asignacion("x <- 1 ensamblar 2.0 ☩")
        self.assertEqual(expresion.tipo_inferido, tipos.ESENCIA)
        self.assertEqual(expresion.hijos[0].tipo_inferido, tipos.CALAVERA)
        self.assertEqual(expresion.hijos[1].tipo_inferido, tipos.ESENCIA)


class PruebasIdentificadoresYLlamadas(unittest.TestCase):

    def test_variable_toma_tipo_de_la_tabla(self):
        tabla = TablaDePrueba().variable("vida", tipos.ESENCIA)
        tipo, errores, _ = inferir_asignacion("x <- vida infestar 2 ☩", tabla)
        self.assertEqual(tipo, tipos.ESENCIA)
        self.assertEqual(errores, [])

    def test_variable_no_declarada_no_genera_error_de_tipos(self):
        tipo, errores, _ = inferir_asignacion("x <- fantasma ensamblar 1 ☩")
        self.assertEqual(tipo, tipos.DESCONOCIDO)
        self.assertEqual(errores, [])

    def test_llamada_usa_tipo_de_retorno(self):
        tabla = TablaDePrueba().ritual("fibonacci", [tipos.CALAVERA], tipos.CALAVERA)
        tipo, errores, _ = inferir_asignacion("x <- fibonacci⟅10⟆ ensamblar 1 ☩", tabla)
        self.assertEqual(tipo, tipos.CALAVERA)
        self.assertEqual(errores, [])

    def test_argumento_con_tipo_incorrecto(self):
        tabla = TablaDePrueba().ritual("fibonacci", [tipos.CALAVERA], tipos.CALAVERA)
        _, errores, _ = inferir_asignacion('x <- fibonacci⟅"diez"⟆ ☩', tabla)
        self.assertEqual(len(errores), 1)
        self.assertIn("argumento", errores[0].mensaje)

    def test_ritual_usado_como_variable(self):
        tabla = TablaDePrueba().ritual("fibonacci", [tipos.CALAVERA], tipos.CALAVERA)
        _, errores, _ = inferir_asignacion("x <- fibonacci ensamblar 1 ☩", tabla)
        self.assertEqual(len(errores), 1)

    def test_rituales_estandar(self):
        casos = {
            "x <- revivir⟅calavera⟆ ☩": tipos.CALAVERA,
            "x <- revivir⟅⟆ ☩": tipos.CANTICO,
            "x <- mundo⟅5⟆ ☩": "fosa calavera",
        }
        for codigo, esperado in casos.items():
            with self.subTest(codigo=codigo):
                tipo, errores, _ = inferir_asignacion(codigo)
                self.assertEqual(tipo, esperado)
                self.assertEqual(errores, [])

    def test_extraer_devuelve_tipo_del_elemento(self):
        tabla = TablaDePrueba().variable("almas", "fosa cantico")
        tipo, _, _ = inferir_asignacion("x <- extraer⟅almas, 1⟆ ☩", tabla)
        self.assertEqual(tipo, tipos.CANTICO)


class PruebasInstrucciones(unittest.TestCase):

    def test_declaracion_valida_y_promocion(self):
        inferencia = InferenciaTipos(TablaDePrueba())
        nodo = primera_instruccion("esencia pi <- 3 ☩")
        self.assertEqual(inferencia.verificar_declaracion(nodo), tipos.ESENCIA)
        self.assertEqual(nodo.tipo_inferido, tipos.ESENCIA)
        self.assertEqual(inferencia.errores, [])

    def test_declaracion_incompatible(self):
        inferencia = InferenciaTipos(TablaDePrueba())
        inferencia.verificar_declaracion(primera_instruccion('calavera a <- "veinte" ☩'))
        self.assertEqual(len(inferencia.errores), 1)

    def test_esencia_no_cabe_en_calavera(self):
        inferencia = InferenciaTipos(TablaDePrueba())
        inferencia.verificar_declaracion(primera_instruccion("calavera a <- 2.5 ☩"))
        self.assertEqual(len(inferencia.errores), 1)

    def test_asignacion(self):
        tabla = TablaDePrueba().variable("a", tipos.CALAVERA)
        inferencia = InferenciaTipos(tabla)

        nodo = primera_instruccion("a <- a ensamblar 1 ☩")
        self.assertEqual(inferencia.verificar_asignacion(nodo), tipos.CALAVERA)
        self.assertEqual(inferencia.errores, [])

        inferencia.verificar_asignacion(primera_instruccion('a <- "texto" ☩'))
        self.assertEqual(len(inferencia.errores), 1)

    def test_sacrificio(self):
        inferencia = InferenciaTipos(TablaDePrueba())
        ritual = primera_instruccion("ritual f⟅⟆ ⚯ calavera ✦ sacrificar 1 ☩ ✧")
        sacrificio = ritual.hijos[-1].hijos[0]

        inferencia.verificar_sacrificio(sacrificio, tipos.CALAVERA)
        self.assertEqual(inferencia.errores, [])

        inferencia.verificar_sacrificio(sacrificio, tipos.CANTICO)
        self.assertEqual(len(inferencia.errores), 1)

        inferencia.verificar_sacrificio(sacrificio, None)
        self.assertEqual(len(inferencia.errores), 2)

    def test_sacrificio_sin_valor_en_ritual_con_retorno(self):
        inferencia = InferenciaTipos(TablaDePrueba())
        ritual = primera_instruccion("ritual f⟅⟆ ⚯ calavera ✦ sacrificar ☩ ✧")
        inferencia.verificar_sacrificio(ritual.hijos[-1].hijos[0], tipos.CALAVERA)
        self.assertEqual(len(inferencia.errores), 1)

    def test_exigir_latido(self):
        inferencia = InferenciaTipos(TablaDePrueba())
        condicional = primera_instruccion("mana⟅1 ensamblar 2⟆ ✦ ✧")
        inferencia.exigir_latido(condicional.hijos[0].hijos[0], "mana")
        self.assertEqual(len(inferencia.errores), 1)


if __name__ == "__main__":
    unittest.main()
