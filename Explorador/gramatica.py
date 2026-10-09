
# Tokens seguros para el modo pánico (delimitadores donde el escáner se recupera)
tokens_seguros = {'☩', '⟆', '✧', '☽', '⟅', '✦', '☾', '\n'}

# Diccionario de palabras reservadas del lenguaje
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
    "restos": "RESTOS"
}

# Operadores de dos caracteres
operadores_dobles = {
    "<-": "ASIGNACION",
    "<=": "MENOR_IGUAL",
    ">=": "MAYOR_IGUAL",
    "==": "IGUAL_QUE",
    "!=": "DIFERENTE_QUE"
}

# Símbolos individuales y operadores de un caracter
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
    '>': "MAYOR_QUE"
}
