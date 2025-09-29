from app.repositories.base_repository import BaseRepository
from app.models.database_models import Conductor, GestorParqueadero, User
from pymongo.database import Database
from typing import Union

class UserRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "usuarios", User)

    def find_all(self) -> list[Union[Conductor, GestorParqueadero]]:
        documents = self.collection.find()
        users = []
        for doc in documents:
            if doc["rol"] == "conductor":
                users.append(Conductor(**doc))
            elif doc["rol"] == "gestor_parqueadero":
                users.append(GestorParqueadero(**doc))
        return users

    def create(self, data: User) -> Union[Conductor, GestorParqueadero]:
        if data.rol == "conductor":
            validated_data = Conductor(**data.dict(by_alias=True))
        elif data.rol == "gestor_parqueadero":
            validated_data = GestorParqueadero(**data.dict(by_alias=True))
        else:
            raise ValueError("Rol no reconocido")

        result = self.collection.insert_one(validated_data.model_dump(by_alias=True))
        resultado = self.find_by_id(str(result.inserted_id))
        return resultado