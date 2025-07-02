from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import faiss
import pickle
import numpy as np
import os
import re

app = FastAPI()


@app.get("/")
def home():
    return {"mensaje": "API para hacer preguntas a tus PDFs. Usa /preguntar?q=tu_pregunta"}

# Función para limpiar texto


def limpiar_texto(texto):
    texto = texto.replace('\n', ' ')
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    return texto


# Rutas de tus modelos y datos
modelo_path = "modelos"

# Cargar modelo de embeddings
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Cargar textos y FAISS
with open(os.path.join(modelo_path, 'textos.pkl'), 'rb') as f:
    textos = pickle.load(f)

with open(os.path.join(modelo_path, 'embeddings.pkl'), 'rb') as f:
    vectores = pickle.load(f)

index = faiss.read_index(os.path.join(modelo_path, 'indice_faiss.index'))

# Preparar pipeline de resumen
resumidor = pipeline("summarization", model="facebook/bart-large-cnn")


@app.get("/preguntar")
def preguntar(q: str = Query(..., description="Pregunta del usuario"), k: int = 3):
    vector_pregunta = modelo.encode([q])
    distancias, indices = index.search(np.array(vector_pregunta), k=k)

    fragmentos = []
    for i in indices[0]:
        f = textos[i]
        if isinstance(f, dict):
            fragmentos.append(f.get('texto', ''))
        else:
            fragmentos.append(str(f))

    # Limpiar fragmentos antes de unirlos
    fragmentos_limpios = [limpiar_texto(f) for f in fragmentos]
    texto_unido = " ".join(fragmentos_limpios)

    resumen = resumidor(texto_unido, max_length=200,
                        min_length=60, do_sample=False)[0]['summary_text']

    return {
        "pregunta": q,
        "fragmentos_relacionados": fragmentos_limpios,
        "resumen": resumen
    }
