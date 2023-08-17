import numpy as np
import pandas as pd

metadata = pd.read_csv("encuestas.csv").drop(columns=["Unnamed: 0"])
transcripciones = pd.read_csv("transcripciones.csv", index_col=0)

def cargar_transcripcion(hash):
    try:
        texto = str(transcripciones.loc[hash]["text"])
    except KeyError:
        print(f"Hash {hash} no encontrado")
        return np.nan
    
    if len(texto) == 2:
        texto = texto[0] + "." + texto[1]
    
    try:
        return float(texto)
    except ValueError as e:
        print(e)
        return np.nan

respuesta_cols = [f"p{i}" for i in range(16)]
cargadas = metadata[respuesta_cols].applymap(cargar_transcripcion)

print("Datos Faltantes:")
print(cargadas.isna().sum() / cargadas.shape[0] * 100)

metadata[respuesta_cols] = cargadas
metadata.to_csv("dataset.csv", index=False)