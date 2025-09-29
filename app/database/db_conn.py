from pymongo import MongoClient
from app.repositories.repositories import UserRepository
import os

def get_db():
    url = os.getenv("MONGO_URL")
    client = MongoClient(url)
    try:    
        db = client["mvp"]
        comprobar_collections(db)
        yield db
    finally:
        client.close()

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
