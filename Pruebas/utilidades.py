"""
Utilidades compartidas por las pruebas: analizar código NecroScrypt y una
tabla de símbolos mínima que cumple el contrato de Comun/simbolos.py.
"""

from Analizador.analizador import Analizador
from Comun.simbolos import PARAMETRO, RITUAL, VARIABLE, Simbolo
from Explorador.explorador import Explorador


def analizar(codigo):
    """Explora y analiza un fragmento de código; falla si tiene errores."""
    explorador = Explorador(codigo)
    tokens = explorador.escanear()
    assert not explorador.errores, explorador.errores
    analizador = Analizador(tokens)
    asa = analizador.analizar()
    assert not analizador.errores, analizador.errores
    return asa


def primera_instruccion(codigo):
    """Retorna el primer nodo del programa analizado."""
    return analizar(codigo).hijos[0]


class TablaDePrueba:
    """
    Tabla plana (sin ámbitos) solo para probar la inferencia de tipos de
    forma aislada. La tabla real la implementa el verificador.
    """

    def __init__(self):
        self.simbolos = {}

    def variable(self, nombre, tipo):
        self.simbolos[nombre] = Simbolo(nombre, tipo, VARIABLE)
        return self

    def parametro(self, nombre, tipo):
        self.simbolos[nombre] = Simbolo(nombre, tipo, PARAMETRO)
        return self

    def ritual(self, nombre, parametros, tipo_retorno=None):
        self.simbolos[nombre] = Simbolo(nombre, tipo_retorno, RITUAL, list(parametros), tipo_retorno)
        return self

    def buscar(self, nombre):
        return self.simbolos.get(nombre)
