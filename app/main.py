import os
from fastapi import Depends, FastAPI, Request
from fastapi.responses import PlainTextResponse
from app.routers import webhook_router
from app.database.db_conn import get_db
from app.models.database_models import User
from app.repositories.repositories import UserRepository

app = FastAPI()

app.include_router(webhook_router.router)

VERIFY_TOKEN = "ClaveSuperSecreta123NoNosRoben"  # Debe coincidir con el que pusiste en Meta



@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/get-db")
async def get_db_info(db = Depends(get_db)):
    return db.list_collection_names()

@app.post("/crear-usuario")
async def crear_usuario(usuario_crear: User, db = Depends(get_db)):
    user_repo = UserRepository(db)
    result = user_repo.create(usuario_crear)
    return result.__str__()