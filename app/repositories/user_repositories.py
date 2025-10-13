from app.repositories.base_repository import BaseRepository
from app.models.database_models import Conductor, GestorParqueadero, User
from pymongo.database import Database
from typing import Union
import time

class ConductorRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "usuarios", Conductor)

    def find_all(self) -> list[Conductor]:
        documents = self.collection.find()
        users = []
        for doc in documents:
            if doc["rol"] == "conductor":
                users.append(Conductor(**doc))
        return users

    def create(self, data: Conductor) -> Conductor:
        validated_data = Conductor(**data.model_dump(by_alias=True))
        result = self.collection.insert_one(validated_data.model_dump(by_alias=True))
        resultado = self.find_by_id(str(result.inserted_id))
        return resultado
    
class GestorParqueaderoRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "usuarios", GestorParqueadero)

    def find_all(self) -> list[GestorParqueadero]:
        documents = self.collection.find()
        users = []
        for doc in documents:
            if doc["rol"] == "gestor_parqueadero":
                users.append(GestorParqueadero(**doc))
        return users

    def create(self, data: GestorParqueadero) -> GestorParqueadero:
        validated_data = GestorParqueadero(**data.model_dump(by_alias=True))
        result = self.collection.insert_one(validated_data.model_dump(by_alias=True))
        resultado = self.find_by_id(str(result.inserted_id))
        return resultado

    def obtener_parqueadero(self, gestor_id: str):
        gestor = self.find_by_id(gestor_id)
        return gestor.parqueadero if gestor else None

class UserRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "usuarios", User)

    def find_all(self) -> list[User]:
        documents = self.collection.find()
        users = [User(**doc) for doc in documents]
        return users

    def create(self, data: Union[Conductor, GestorParqueadero]) -> User:
        validated_data = User(**data.model_dump(by_alias=True))
        result = self.collection.insert_one(validated_data.model_dump(by_alias=True))
        resultado = self.find_by_id(str(result.inserted_id))
        return resultado
    
    def actualizar_estado_chat(self, user_id: str, paso_actual: str) -> User:
        update_data = {
            "estado_chat.ultima_interaccion": time.strftime("%Y-%m-%d %H:%M:%S"),
            "estado_chat.paso_actual": paso_actual
        }
        self.collection.update_one({"_id": user_id}, {"$set": update_data})
        return self.find_by_id(user_id)

    def actualizar_estado_registro(self, user_id: str, estado_registro: str) -> User:
        update_data = {
            "estado_registro": estado_registro
        }
        self.collection.update_one({"_id": user_id}, {"$set": update_data})
        return self.find_by_id(user_id)
    def actualizar_nombre(self, user_id: str, nombre: str) -> User:
        update_data = {
            "name": nombre
        }
        self.collection.update_one({"_id": user_id}, {"$set": update_data})
        return self.find_by_id(user_id)