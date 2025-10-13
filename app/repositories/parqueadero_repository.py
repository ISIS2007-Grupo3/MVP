from app.repositories.base_repository import BaseRepository
from app.models.database_models import Parqueadero
import time
class ParqueaderoRepository(BaseRepository):   
    def __init__(self, db):
          super().__init__(db, "parqueaderos", Parqueadero)

    def find_by_name(self, name: str) -> Parqueadero | None:
        data = self.collection.find_one({"name": name})
        if data:
            return self.model(**data)
        return None
    
    def create(self, data) -> Parqueadero | dict:
         if self.find_by_name(data["name"]):
             return {"error": "Parqueadero con este nombre ya existe"}
         data["ultima_actualizacion"] = time.strftime("%Y-%m-%d %H:%M:%S")
         return super().create(data)

    def find_with_available_spots(self) -> list[Parqueadero]:
        documents = self.collection.find({"tiene_cupos": True}, sort=[("ultima_actualizacion", -1)])
        parqueaderos = []
        for doc in documents:
            parqueaderos.append(Parqueadero(**doc))
        return parqueaderos
    
    def actualizar_cupos(self, parking_id: str, cupos_libres: str, tiene_cupos: bool) -> Parqueadero:
        update_data = {
            "cupos_libres": cupos_libres,
            "tiene_cupos": tiene_cupos,
            "ultima_actualizacion": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.collection.update_one({"_id": parking_id}, {"$set": update_data})
        return self.find_by_id(parking_id)