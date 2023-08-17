Un scrapper para las encuestas docentes de la facultad de Exactas de la UBA. El objetivo es producir un CSV con las materias dictadas en un cuatrimestre, y las respuestas de los alumnos a las preguntas de la encuesta.

La lista de preguntas se encuentra en el archivo `preguntas.json`. En el dataset se numeran de p0 a p15.

# Instalación
Para instalar en Ubuntu o Debian, simplemente correr el script `install.sh` con permisos de root.

# Uso
Viendo la [página de la encuestas](https://encuestas-finales.exactas.uba.ar/), las respuesta vienen en formato imagen, como en [este ejemplo](https://encuestas-finales.exactas.uba.ar/img/na/m6242u502.png). Por lo tanto, el scrapeo se divide en dos partes: la descarga de las imágenes de las encuestas, y el reconocimiento de las mismas. Lamentablemente, el reconocimiento de las imágenes no es perfecto, por lo que es necesario revisar los resultados manualmente.

La pipeline es así:

- `listar_materias.py` va a la página principal y obtiene un listado de todas las materias. Se guardan en un archivo `materias.json`.
- `scrap.py` baja la metadata y las imágenes de las materias listadas. Las imágenes se guardan en una carpeta `respuestas`, y la data en `encuestas.csv`. 
- `transcribir.py` corre el OCR sobre las imágenes, y guarda los resultados en `transcripciones.csv`.
- `juntar.py` junta los resultados de `encuestas.csv` y `transcripciones.csv` en un solo archivo `dataset.csv`.

# TODO

~~- Reconocer las imagenes descargas con OCR~~
- Sacar el overkill que es el OCR
- Juntar toda la pipeline en un solo script