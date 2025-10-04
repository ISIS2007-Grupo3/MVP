from pymongo import MongoClient
from app.repositories.user_repositories import UserRepository
import os

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["mvp"]

def get_db():
    comprobar_collections(db)
    return db

def comprobar_collections(db):
    colecciones = db.list_collection_names()
    if "mensajes" not in colecciones:
        db.create_collection("mensajes")
    if "usuarios" not in colecciones:
        db.create_collection("usuarios")
    if "conversaciones" not in colecciones:
        db.create_collection("conversaciones")
    if "parqueaderos" not in colecciones:
        db.create_collection("parqueaderos")

def get_usuario(db, wa_id: str):
    user_repo = UserRepository(db)
    return user_repo.find_by_id(wa_id)
