from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np

# Inicializar FastAPI
app = FastAPI()


@app.get("/")
def home():
    return {"mensaje": "API para hacer preguntas a tus PDFs. Usa /preguntar?q=tu_pregunta"}


# Cargar modelo
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Cargar embeddings y FAISS
with open('modelos/textos.pkl', 'rb') as f:
    textos = pickle.load(f)

with open('modelos/embeddings.pkl', 'rb') as f:
    vectores = pickle.load(f)

index = faiss.read_index('modelos/indice_faiss.index')


@app.get("/preguntar")
def preguntar(q: str = Query(..., description="Pregunta del usuario"), k: int = 3):
    vector_pregunta = modelo.encode([q])
    distancias, indices = index.search(np.array(vector_pregunta), k=k)
    fragmentos = [textos[i] for i in indices[0]]
    return {
        "pregunta": q,
        "fragmentos_relacionados": fragmentos
    }
