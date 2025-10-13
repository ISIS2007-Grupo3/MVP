from app.repositories.base_repository import BaseRepository
from app.models.database_models import Parqueadero
from app.utils.tiempo_utils import obtener_tiempo_bogota
class ParqueaderoRepository(BaseRepository):   
    def __init__(self, db):
          super().__init__(db, "parqueaderos", Parqueadero)

    def find_by_name(self, name: str) -> Parqueadero:
        data = self.collection.find_one({"name": name})
        if data:
            return self.model(**data)
        return None
    
    def create(self, data) -> Parqueadero | dict:
         if self.find_by_name(data["name"]):
             return {"error": "Parqueadero con este nombre ya existe"}
         data["ultima_actualizacion"] = obtener_tiempo_bogota()
         return super().create(data)

    def find_with_available_spots(self) -> list[Parqueadero]:
        documents = self.collection.find({"tiene_cupos": True}, sort=[("ultima_actualizacion", -1)])
        parqueaderos = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])  # Convertir ObjectId a string
            parqueaderos.append(Parqueadero(**doc))
        return parqueaderos
    
    def actualizar_cupos(self, parking_id: str, cupos_libres: str, tiene_cupos: bool) -> Parqueadero:
        update_data = {
            "cupos_libres": cupos_libres,
            "tiene_cupos": tiene_cupos,
            "ultima_actualizacion": obtener_tiempo_bogota()
        }
        self.collection.update_one({"_id": parking_id}, {"$set": update_data})
        return self.find_by_id(parking_id)
    
    def actualizar_cupos_con_rango(self, parking_id: str, cupos_libres: str, tiene_cupos: bool, 
                                   rango_cupos: str, estado_ocupacion: str) -> Parqueadero:
        """Actualiza cupos incluyendo rango y descripción del estado"""
        update_data = {
            "cupos_libres": cupos_libres,
            "tiene_cupos": tiene_cupos,
            "rango_cupos": rango_cupos,
            "estado_ocupacion": estado_ocupacion,
            "ultima_actualizacion": obtener_tiempo_bogota()
        }
        self.collection.update_one({"_id": parking_id}, {"$set": update_data})
        return self.find_by_id(parking_id)
    
    def actualizar_cupos_con_notificacion(self, parking_id: str, cupos_libres: str, tiene_cupos: bool, 
                                          rango_cupos: str, estado_ocupacion: str, notification_service) -> dict:
        """Actualiza cupos con rango y envía notificaciones si hay cupos disponibles"""
        parqueadero = self.actualizar_cupos_con_rango(
            parking_id, cupos_libres, tiene_cupos, rango_cupos, estado_ocupacion
        )
        
        # Si hay cupos disponibles, notificar a suscriptores
        notificaciones_enviadas = 0
        if tiene_cupos and int(cupos_libres) > 0:
            notificaciones_enviadas = notification_service.notificar_cupo_liberado(parking_id)
        
        return {
            "parqueadero": parqueadero.model_dump(by_alias=True),
            "notificaciones_enviadas": notificaciones_enviadas
        }