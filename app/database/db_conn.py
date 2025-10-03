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
    if "mensajes" not in db.list_collection_names():
        db.create_collection("mensajes")
    if "usuarios" not in db.list_collection_names():
        db.create_collection("usuarios")
    if "conversaciones" not in db.list_collection_names():
        db.create_collection("conversaciones")
    
def get_usuario(db, wa_id: str):
    user_repo = UserRepository(db)
    return user_repo.find_by_id(wa_id)
