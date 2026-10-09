# Errores Léxicos de NecroScrypt

El explorador detecta errores léxicos y se recupera mediante **modo pánico** descartando caracteres hasta encontrar un token seguro (`☩`, `✦`, `✧`, `⟅`, `⟆`, `☾`, `☽` o salto de línea).

## Tipos de errores

| Código | Error | Causa | Ejemplo incorrecto |
| :--- | :--- | :--- | :--- |
| **ERR-01** | Carácter no válido | Símbolo inexistente en el lenguaje | `calavera x @ 5 ☩` |
| **ERR-02** | Cadena sin cerrar | Falta la comilla doble de cierre (`"`) | `"hola mundo ☩` |
| **ERR-03** | Comentario sin cerrar | Falta el cierre del comentario (`~~`) | `~~ comentario abierto` |
| **ERR-04** | Decimal incompleto | Punto sin dígitos decimales | `3. ☩` |
| **ERR-05** | Múltiples puntos | Número con más de un punto | `1.5.0 ☩` |
| **ERR-06** | Identificador con número | Variable que inicia con un dígito | `1alma ☩` |
| **ERR-07** | Operador no válido | Operador mal formado o incompleto | `vida ! 0 ☩` |
