"""
Contrato compartido entre la tabla de símbolos y el resto del verificador.

Este archivo NO implementa la tabla de símbolos: solo fija la forma de los
símbolos y la única operación que necesitan las demás partes (inferencia de
tipos, generador). La implementación real (pila de ámbitos, redeclaraciones,
impresión parcial) queda a cargo de quien construya la tabla, siempre que
respete esta interfaz.
"""

from dataclasses import dataclass, field
from typing import List, Optional

try:
    from typing import Protocol
except ImportError:  # pragma: no cover - Python < 3.8
    Protocol = object


# Categorías posibles de un símbolo
VARIABLE = "variable"
PARAMETRO = "parametro"
RITUAL = "ritual"


@dataclass
class Simbolo:
    """
    Información de un identificador declarado en el programa.

    Atributos:
        nombre: Nombre del identificador tal como aparece en el código.
        tipo: Tipo de la variable ('calavera', 'fosa cantico', ...).
              En los rituales se usa el tipo de retorno.
        categoria: VARIABLE, PARAMETRO o RITUAL.
        parametros: Solo rituales. Tipos de los parámetros en orden.
        tipo_retorno: Solo rituales. Tipo que devuelve, o None si no devuelve nada.
        nodo: Nodo del ASA donde se declaró (para mostrar la definición).
    """

    nombre: str
    tipo: Optional[str]
    categoria: str = VARIABLE
    parametros: List[str] = field(default_factory=list)
    tipo_retorno: Optional[str] = None
    nodo: object = None


class TablaSimbolos(Protocol):
    """
    Interfaz mínima que la inferencia de tipos espera de la tabla de símbolos.
    """

    def buscar(self, nombre: str) -> Optional[Simbolo]:
        """
        Busca un identificador desde el ámbito actual hacia el global.

        Retorna:
            Simbolo: El símbolo visible con ese nombre, o None si no existe.
        """
        ...
