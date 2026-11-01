# Explorador de NecroScrypt

Esta carpeta tiene el explorador para NecroScrypt, el lenguaje del grupo de Zapateros para el curso de Compiladores.
El punto de entrada es `transpilador.py`, que lee archivos con extensión `.ns`, separa el texto en tokens y avisa si se topa con caracteres o símbolos que no pertenecen al lenguaje.

## Estructura de la carpeta

- `explorador.py`: Es el "Scanner" o explorador principal. Va leyendo el código carácter por carácter, reconoce palabras reservadas, números o símbolos especiales, y aplica modo pánico si hay algo roto para seguir leyendo.
- `errores.py`: Guarda la información básica de cualquier error (el mensaje, la línea y la columna).
- `asa.py`: Define la clase `Token` que genera el explorador.
- `gramatica.py`: Palabras reservadas, operadores y símbolos del lenguaje.
- `ERRORES.md`: Lista los errores léxicos soportados, cómo se recupera el escáner y sugerencias para corregirlos.
- `Ejemplos/`: Pruebas rápidas en `.ns`, como `ejemplo.ns` (código limpio) y `error_uno.ns` (para probar que salten los errores).

## Cómo ejecutarlo

Para probar un archivo válido:

```bash
python transpilador.py Explorador/Ejemplos/ejemplo.ns
```

O para ver cómo reacciona ante errores:

```bash
python transpilador.py Explorador/Ejemplos/error_uno.ns
```
