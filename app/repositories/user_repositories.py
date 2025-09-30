from app.repositories.base_repository import BaseRepository
from app.models.database_models import Conductor, GestorParqueadero, User
from pymongo.database import Database
from typing import Union

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