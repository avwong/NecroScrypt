"""
Tablas léxicas y gramaticales para NecroScrypt.

Contiene las palabras reservadas, operadores, símbolos especiales y nombres
amigables usados por el explorador y el analizador.
"""

# Tokens seguros para el modo pánico del explorador (delimitadores de recuperación)
tokens_seguros = {'☩', '⟆', '✧', '☽', '⟅', '✦', '☾', '\n'}

# Diccionario de palabras reservadas del lenguaje NecroScrypt
palabras_reservadas = {
    "ritual": "RITUAL",
    "sacrificar": "SACRIFICAR",
    "mana": "MANA",
    "sin mana": "SIN_MANA",
    "sin": "SIN",
    "convocar": "CONVOCAR",
    "en": "EN",
    "persistir": "PERSISTIR",
    "calavera": "CALAVERA",
    "cantico": "CANTICO",
    "esencia": "ESENCIA",
    "latido": "LATIDO",
    "ceniza": "CENIZA",
    "fosa": "FOSA",
    "invocar": "INVOCAR",
    "revivir": "REVIVIR",
    "y": "Y",
    "o": "O",
    "vivo": "VIVO",
    "muerto": "MUERTO",
    "ensamblar": "ENSAMBLAR",
    "mutilar": "MUTILAR",
    "infestar": "INFESTAR",
    "desmembrar": "DESMEMBRAR",
    "restos": "RESTOS",
}

# Operadores de dos caracteres (compuestos)
operadores_dobles = {
    "<-": "ASIGNACION",
    "<=": "MENOR_IGUAL",
    ">=": "MAYOR_IGUAL",
    "==": "IGUAL_QUE",
    "!=": "DIFERENTE_QUE",
}

# Símbolos individuales y delimitadores de un solo carácter
simbolos = {
    '☩': "FIN_INSTRUCCION",
    '⟅': "PARENTESIS_IZQUIERDO",
    '⟆': "PARENTESIS_DERECHO",
    '✦': "INICIO_BLOQUE",
    '✧': "FIN_BLOQUE",
    '☾': "CORCHETE_IZQUIERDO",
    '☽': "CORCHETE_DERECHO",
    '⚯': "ASIGNACION_RETORNO",
    ',': "COMA",
    '&': "REFERENCIA",
    '<': "MENOR_QUE",
    '>': "MAYOR_QUE",
}

# Tipos primitivos válidos en NecroScrypt
TIPOS_PRIMITIVOS = (
    "CALAVERA",
    "CANTICO",
    "ESENCIA",
    "LATIDO",
)

# Palabras clave con las que puede comenzar una declaración
INICIOS_DE_DECLARACION = (
    "CALAVERA",
    "CANTICO",
    "ESENCIA",
    "LATIDO",
    "CENIZA",
    "FOSA",
)

# Nombres amigables para mostrar en los mensajes de error al programador
NOMBRES_AMIGABLES = {
    "FIN_INSTRUCCION": "☩",
    "INICIO_BLOQUE": "✦",
    "FIN_BLOQUE": "✧",
    "PARENTESIS_IZQUIERDO": "⟅",
    "PARENTESIS_DERECHO": "⟆",
    "CORCHETE_IZQUIERDO": "☾",
    "CORCHETE_DERECHO": "☽",
    "ASIGNACION": "<-",
    "ASIGNACION_RETORNO": "⚯",
    "COMA": ",",
    "IDENTIFICADOR": "un identificador",
    "RITUAL": "ritual",
    "SACRIFICAR": "sacrificar",
    "MANA": "mana",
    "SIN_MANA": "sin mana",
    "SIN": "sin",
    "CONVOCAR": "convocar",
    "EN": "en",
    "PERSISTIR": "persistir",
    "CALAVERA": "calavera",
    "CANTICO": "cantico",
    "ESENCIA": "esencia",
    "LATIDO": "latido",
    "CENIZA": "ceniza",
    "FOSA": "fosa",
    "INVOCAR": "invocar",
    "REVIVIR": "revivir",
    "ENTERO": "un número entero",
    "DECIMAL": "un número decimal",
    "CADENA": "un texto entre comillas",
    "VIVO": "vivo",
    "MUERTO": "muerto",
    "EOF": "fin de archivo",
}
