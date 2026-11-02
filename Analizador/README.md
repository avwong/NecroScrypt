# Explorador de NecroScrypt

Esta carpeta tiene el explorador para NecroScrypt.
El punto de entrada es `transpilador.py`, que lee archivos con extensión `.ns`,
separa el texto en tokens y avisa si se topa con caracteres o símbolos que no pertenecen al lenguaje.

## Estructura de la carpeta

- `analizador.py`: Es el "Parser",  Va leyendo el código carácter por carácter, reconoce palabras reservadas, números o símbolos especiales, y aplica modo pánico si hay algo roto para seguir leyendo.
