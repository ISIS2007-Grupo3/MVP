from app.repositories.base_repository import BaseRepository
from app.models.database_models import Suscripcion
from pymongo.database import Database
from app.utils.tiempo_utils import obtener_tiempo_bogota
from typing import List, Optional

class SuscripcionRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "suscripciones", Suscripcion)

    def create_suscripcion(self, conductor_id: str, parqueadero_id: Optional[str] = None) -> Suscripcion:
        """Crea una nueva suscripción"""
        # Verificar si ya existe una suscripción activa
        existing = self.find_active_suscripcion(conductor_id, parqueadero_id)
        if existing:
            return existing
        
        data = {
            "conductor_id": conductor_id,
            "parqueadero_id": parqueadero_id,
            "fecha_suscripcion": obtener_tiempo_bogota(),
            "activa": True
        }
        return super().create(data)

    def find_active_suscripcion(self, conductor_id: str, parqueadero_id: Optional[str] = None) -> Optional[Suscripcion]:
        """Busca una suscripción activa específica"""
        filter_dict = {"conductor_id": conductor_id, "activa": True}
        if parqueadero_id:
            filter_dict["parqueadero_id"] = parqueadero_id
        else:
            filter_dict["parqueadero_id"] = None
            
        document = self.collection.find_one(filter_dict)
        return self.model(**document) if document else None

    def find_suscripciones_by_conductor(self, conductor_id: str) -> List[Suscripcion]:
        """Obtiene todas las suscripciones activas de un conductor"""
        documents = self.collection.find({"conductor_id": conductor_id, "activa": True})
        return [self.model(**doc) for doc in documents]

    def find_suscripciones_by_parqueadero(self, parqueadero_id: str) -> List[Suscripcion]:
        """Obtiene todas las suscripciones activas para un parqueadero específico"""
        documents = self.collection.find({
            "$or": [
                {"parqueadero_id": parqueadero_id, "activa": True},
                {"parqueadero_id": None, "activa": True}  # Suscripciones globales
            ]
        })
        return [self.model(**doc) for doc in documents]

    def desactivar_suscripcion(self, conductor_id: str, parqueadero_id: Optional[str] = None) -> bool:
        """Desactiva una suscripción específica"""
        filter_dict = {"conductor_id": conductor_id, "activa": True}
        if parqueadero_id:
            filter_dict["parqueadero_id"] = parqueadero_id
        else:
            filter_dict["parqueadero_id"] = None
            
        result = self.collection.update_one(filter_dict, {"$set": {"activa": False}})
        return result.modified_count > 0

    def desactivar_todas_suscripciones(self, conductor_id: str) -> int:
        """Desactiva todas las suscripciones de un conductor"""
        result = self.collection.update_many(
            {"conductor_id": conductor_id, "activa": True},
            {"$set": {"activa": False}}
        )
        return result.modified_count