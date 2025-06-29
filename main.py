from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
import os
import requests

app = FastAPI()


@app.get("/")
def home():
    return {"mensaje": "API para hacer preguntas a tus PDFs. Usa /preguntar?q=tu_pregunta"}


# URLs públicas de Blob Storage
urls = {
    "textos.pkl": "https://eduardo56745.blob.core.windows.net/eduardo56745/textos.pkl",
    "embeddings.pkl": "https://eduardo56745.blob.core.windows.net/eduardo56745/embeddings.pkl",
    "indice_faiss.index": "https://eduardo56745.blob.core.windows.net/eduardo56745/indice_faiss.index"
}

# Carpeta local para guardar archivos
modelo_path = "modelos"
os.makedirs(modelo_path, exist_ok=True)


def descargar_archivo(nombre_archivo):
    ruta_local = os.path.join(modelo_path, nombre_archivo)
    if not os.path.exists(ruta_local):
        print(f"Descargando {nombre_archivo}...")
        r = requests.get(urls[nombre_archivo])
        r.raise_for_status()
        with open(ruta_local, "wb") as f:
            f.write(r.content)
    else:
        print(f"{nombre_archivo} ya existe, no se descarga.")


# Descargar archivos si no existen
for archivo in urls.keys():
    descargar_archivo(archivo)

# Cargar modelo y datos
modelo = SentenceTransformer('all-MiniLM-L6-v2')

with open(os.path.join(modelo_path, 'textos.pkl'), 'rb') as f:
    textos = pickle.load(f)

with open(os.path.join(modelo_path, 'embeddings.pkl'), 'rb') as f:
    vectores = pickle.load(f)

index = faiss.read_index(os.path.join(modelo_path, 'indice_faiss.index'))


@app.get("/preguntar")
def preguntar(q: str = Query(..., description="Pregunta del usuario"), k: int = 3):
    vector_pregunta = modelo.encode([q])
    distancias, indices = index.search(np.array(vector_pregunta), k=k)
    fragmentos = [textos[i] for i in indices[0]]
    return {
        "pregunta": q,
        "fragmentos_relacionados": fragmentos
    }
