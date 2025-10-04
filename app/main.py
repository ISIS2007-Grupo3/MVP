import os
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import Response
from app.routers import webhook_router
from app.database.db_conn import get_db
from app.models.database_models import Parqueadero, User
from app.repositories.user_repositories import ConductorRepository, UserRepository
from app.repositories.parqueadero_repository import ParqueaderoRepository

app = FastAPI()

app.include_router(webhook_router.router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/get-db")
async def get_db_info(db = Depends(get_db)):
    return db.list_collection_names()

@app.post("/crear-usuario")
async def crear_usuario(usuario_crear: User, db = Depends(get_db)):
    user_repo = ConductorRepository(db)
    result = user_repo.create(usuario_crear.model_dump(by_alias=True))
    return result.model_dump(by_alias=True)

@app.get("/usuarios")
async def listar_usuarios(db = Depends(get_db)):
    user_repo = UserRepository(db)
    usuarios = user_repo.find_all()
    return [u.model_dump(by_alias=True) for u in usuarios]

@app.post("/crear-parqueadero")
async def crear_parqueadero(parqueadero_crear: Parqueadero, db = Depends(get_db)):
    parqueadero_repo = ParqueaderoRepository(db)
    result = parqueadero_repo.create(parqueadero_crear.model_dump(by_alias=True))
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result.model_dump(by_alias=True)