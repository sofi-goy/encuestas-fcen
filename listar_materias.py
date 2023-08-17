import requests
from bs4 import BeautifulSoup as bs

BASE = "https://encuestas-finales.exactas.uba.ar/"
INICIO = BASE + "periodos.html"

def lst(lid, p):
    print("LST", lid, p)
    url = BASE + "lists/l_"  + lid + "_" + p + ".html"
    return requests.get(url).text

def parsear_materias():
    PAGINAS = 74
    materias = {}
    for i in range(PAGINAS):
        html = lst("mats", str(i))
        for materia in bs(html, "html.parser").find("ul").find_all("li"):
            # Save materia withthetext as a key and the link as a value
            link = materia.find("a")
            materias[link.text] = BASE + link["href"]

    import json
    with open("materias.json", "w") as f:
        json.dump(materias, f)

parsear_materias()