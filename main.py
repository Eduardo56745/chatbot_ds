from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
import os

app = FastAPI()

# Rutas de los archivos
MODELO_PATH = "modelos"
TEXTOS_PATH = os.path.join(MODELO_PATH, 'textos.pkl')
EMBEDDINGS_PATH = os.path.join(MODELO_PATH, 'embeddings.pkl')
INDEX_PATH = os.path.join(MODELO_PATH, 'indice_faiss.index')

# Variables globales (sin inicializar)
modelo = None
textos = None
index = None


def cargar_recursos():
    global modelo, textos, index

    if modelo is None:
        modelo = SentenceTransformer('all-MiniLM-L6-v2')
    if textos is None:
        with open(TEXTOS_PATH, 'rb') as f:
            textos = pickle.load(f)
    if index is None:
        index = faiss.read_index(INDEX_PATH)


@app.get("/")
def home():
    return {
        "mensaje": "API para preguntas a tus PDFs.\nUsa /preguntar?q=tu_pregunta"
    }


@app.get("/preguntar")
def preguntar(
    q: str = Query(..., description="Tu pregunta"),
    k: int = Query(3, description="Número de resultados")
):
    cargar_recursos()

    vector_pregunta = modelo.encode([q])
    distancias, indices = index.search(np.array(vector_pregunta), k=k)
    fragmentos = [textos[i] for i in indices[0]]

    return {
        "pregunta": q,
        "fragmentos_relacionados": fragmentos
    }
