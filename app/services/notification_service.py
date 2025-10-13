from app.repositories.suscripcion_repository import SuscripcionRepository
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.services.whatsapp_message_service import WhatsAppMessageService
from app.utils.tiempo_utils import formatear_tiempo_para_usuario
from pymongo.database import Database
from typing import List

class NotificationService:
    def __init__(self, db: Database):
        self.suscripcion_repo = SuscripcionRepository(db)
        self.parqueadero_repo = ParqueaderoRepository(db)
        self.message_service = WhatsAppMessageService(db)

    def notificar_cupo_liberado(self, parqueadero_id: str) -> int:
        """
        Notifica a todos los suscriptores cuando se libera un cupo
        Retorna el número de notificaciones enviadas
        """
        # Obtener información del parqueadero
        parqueadero = self.parqueadero_repo.find_by_id(parqueadero_id)
        if not parqueadero:
            return 0

        # Obtener suscriptores para este parqueadero
        suscripciones = self.suscripcion_repo.find_suscripciones_by_parqueadero(parqueadero_id)
        
        # Crear mensaje de notificación
        mensaje = self.message_service.crear_notificacion_cupo_liberado(parqueadero)
        
        # Enviar notificaciones
        notificaciones_enviadas = 0
        for suscripcion in suscripciones:
            try:
                self.message_service.enviar_notificacion_cupo(suscripcion.conductor_id, mensaje)
                notificaciones_enviadas += 1
            except Exception as e:
                print(f"Error enviando notificación a {suscripcion.conductor_id}: {e}")
        
        return notificaciones_enviadas

    def suscribir_conductor(self, conductor_id: str, parqueadero_id: str = None) -> dict:
        """
        Suscribe un conductor a notificaciones
        Si parqueadero_id es None, se suscribe a todos los parqueaderos
        """
        try:
            suscripcion = self.suscripcion_repo.create_suscripcion(conductor_id, parqueadero_id)
            
            if parqueadero_id:
                parqueadero = self.parqueadero_repo.find_by_id(parqueadero_id)
                self.message_service.confirmar_suscripcion_especifica(conductor_id, parqueadero.name)
            else:
                self.message_service.confirmar_suscripcion_global(conductor_id)
            
            return {"success": True, "message": "Suscripción exitosa"}
            
        except Exception as e:
            return {"success": False, "message": f"Error en suscripción: {str(e)}"}

    def desuscribir_conductor(self, conductor_id: str, parqueadero_id: str = None) -> dict:
        """
        Desuscribe un conductor
        Si parqueadero_id es None, desuscribe de todos
        """
        try:
            if parqueadero_id:
                # Desuscribir de un parqueadero específico
                success = self.suscripcion_repo.desactivar_suscripcion(conductor_id, parqueadero_id)
                if success:
                    parqueadero = self.parqueadero_repo.find_by_id(parqueadero_id)
                    self.message_service.confirmar_desuscripcion_especifica(conductor_id, parqueadero.name)
                    return {"success": True, "message": "Desuscripción exitosa", "had_subscriptions": True}
                else:
                    self.message_service.error_sin_suscripciones(conductor_id)
                    return {"success": False, "message": "Sin suscripciones", "had_subscriptions": False}
            else:
                # Desuscribir de todos
                count = self.suscripcion_repo.desactivar_todas_suscripciones(conductor_id)
                if count > 0:
                    self.message_service.confirmar_desuscripcion_total(conductor_id)
                    return {"success": True, "message": "Desuscripción exitosa", "had_subscriptions": True}
                else:
                    self.message_service.error_sin_suscripciones(conductor_id)
                    return {"success": False, "message": "Sin suscripciones", "had_subscriptions": False}
            
        except Exception as e:
            return {"success": False, "message": f"Error en desuscripción: {str(e)}", "had_subscriptions": None}

    def listar_suscripciones_conductor(self, conductor_id: str) -> List[dict]:
        """Lista las suscripciones activas de un conductor"""
        suscripciones = self.suscripcion_repo.find_suscripciones_by_conductor(conductor_id)
        result = []
        
        for suscripcion in suscripciones:
            if suscripcion.parqueadero_id:
                parqueadero = self.parqueadero_repo.find_by_id(suscripcion.parqueadero_id)
                result.append({
                    "tipo": "específico",
                    "parqueadero": parqueadero.name if parqueadero else "Parqueadero no encontrado",
                    "fecha": formatear_tiempo_para_usuario(suscripcion.fecha_suscripcion)
                })
            else:
                result.append({
                    "tipo": "global",
                    "parqueadero": "Todos los parqueaderos",
                    "fecha": formatear_tiempo_para_usuario(suscripcion.fecha_suscripcion)
                })
        
        return result