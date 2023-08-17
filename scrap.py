import os
import cv2
import json
import hashlib
import pandas as pd

import requests
from bs4 import BeautifulSoup as bs

from queue import Queue
from threading import Thread

BASE = "https://encuestas-finales.exactas.uba.ar/"

respuestas_hash = {}

ordinales = {"1": "Primer", "2": "Segundo", "3": "Tercero", "4":"Cuarto"}
epocas = {"i": "Invierno", "v": "Verano", "c": "Cuatrimestre", "b": "Bimestre"}

def parsear_periodo(periodo):
    if len(periodo) == 5:
        if periodo[0] == "a":
            return None, None

        epoca = epocas[periodo[0]]
        año = periodo[1:]
    
    elif len(periodo) == 6:
        epoca = ordinales[periodo[0]] + " " + epocas[periodo[1]]
        año = periodo[2:]

    else:
        print("Error en el formato del periodo", periodo)
        return None, None

    return epoca, año

def parsear_respuestas(id_, url):
    global respuestas_hash
    PREGUNTAS = 17
    imagen = requests.get(url).content
    with open(f"/tmp/{id_}.png", "wb") as f:
        f.write(imagen)

    img = cv2.imread(f"/tmp/{id_}.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    width = img.shape[1]
    width_res = width // PREGUNTAS + 1

    respuestas = {}
    for i in range(PREGUNTAS-1):
        respuesta = img[:,width_res*i:width_res*(i+1)-1]
        hasheada = hashlib.md5(respuesta.data.tobytes()).hexdigest()
        if not hasheada in respuestas_hash:
            respuestas_hash[hasheada] = respuesta
            cv2.imwrite(f"respuestas/{hasheada}.png", respuesta)   

        respuestas[f"p{i}"] = hasheada
    
    return respuestas

def parsear_comentarios(id_materia, id_cuatri):
    url = BASE + "cma/" + id_materia + id_cuatri + ".html"
    soup = bs(requests.get(url).text, "html.parser")
    
    comentarios = []
    for comentario in soup.find_all("div", class_="cm"):
        comentarios.append(comentario.text.replace('\r', '\n'))

    return comentarios

def parsear_materia(materia, url):
    soup = bs(requests.get(url).text, "html.parser")

    id_materia = url.split("/")[-1].split(".")[0]
    
    departamento = None
    encuestas = []
    
    for bold in soup.find_all("b"):
        if bold.text == "Departamento:":
            departamento = bold.next_sibling.next_sibling.text
    
    # Find tr elements with non empty ids and withoout  display none
    for fila in soup.find_all("tr"):
        if not fila.has_attr("id"):
            continue
        if fila.has_attr("style"):
            continue

        id_cuatri = fila.attrs["id"]
        periodo = fila.find_all("td")[0].text
        periodo = parsear_periodo(periodo)
        foto_url = '/'.join(fila.find("img")["src"].split("/")[1:])

        respuestas = parsear_respuestas(id_materia + id_cuatri, BASE + foto_url)
        comentarios = parsear_comentarios(id_materia, id_cuatri)

        encuestas.append({
            "materia": materia,
            "departamento": departamento,
            "epoca": periodo[0],
            "año": periodo[1],
            "comentarios": comentarios,
            **respuestas
        })
    
    return encuestas

def worker():
    global scrapeadas, materias_queue

    indice = 0
    encuestas = []
    while not materias_queue.empty():
        materia, url = materias_queue.get()

        encuestas +=  parsear_materia(materia, url)
        scrapeadas += 1
        print(f"Materia {materia} ({scrapeadas}/{total})")
        indice = (indice + 1) % 10
        if indice % 10 == 0:
            print("Guardando...")
            df = pd.DataFrame(encuestas)
            df.to_csv("encuestas.csv", mode="a", header=not os.path.exists("encuestas.csv"))
            encuestas = []
        

encuestas = []
indice = 0
try:
    materias = json.load(open("materias.json"))
except FileNotFoundError:
    print("No se encontró el archivo materias.json, correr listar_materias.py")
    quit()

if os.path.exists("encuestas.csv"):
    parseadas = pd.read_csv("encuestas.csv")
    materias = {k: v for k, v in materias.items() if k not in parseadas["materia"].unique()}

os.makedirs("respuestas", exist_ok=True)

total = len(materias)
scrapeadas = 0
materias_queue = Queue()
for materia, url in materias.items():
    materias_queue.put((materia, url))

workers = []
for i in range(50):
    t = Thread(target=worker)
    t.start()
    workers.append(t)

try:
    for t in workers:
        t.join()
except KeyboardInterrupt:
    print("Me cerraron!")
    quit()