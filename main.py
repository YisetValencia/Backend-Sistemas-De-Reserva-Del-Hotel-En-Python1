"""
Arranca la API FastAPI (uvicorn).rando e

  python main.py

Documentación interactiva: http://127.0.0.1:8000/docs

Para crear tablas en la base de datos, usa: python init_db.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)