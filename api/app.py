from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.config import create_tables

from api import servicios_adicionales, usuario, habitacion, reserva, tipo_habitacion, reserva_servicios


@asynccontextmanager
async def lifespan(_app: FastAPI):
    
    import entities.habitacion  
    import entities.reserva_servicios  
    import entities.reserva  
    import entities.servicios_adicionales  
    import entities.tipo_habitacion  
    import entities.usuario  

    create_tables()
    yield


app = FastAPI(title="API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-y7g3.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(habitacion.router)
app.include_router(reserva_servicios.router)
app.include_router(reserva.router)
app.include_router(servicios_adicionales.router)
app.include_router(tipo_habitacion.router)
app.include_router(usuario.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}