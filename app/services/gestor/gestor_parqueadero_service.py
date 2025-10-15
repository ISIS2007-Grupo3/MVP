"""
Servicio especializado para información de parqueaderos (gestor)
"""
from app.services.message.mensaje_parqueadero_service import MensajeParqueaderoService
from app.services.message.mensaje_error_service import MensajeErrorService
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.repositories.user_repositories import GestorParqueaderoRepository


class GestorParqueaderoService:
    """
    Servicio enfocado en consultar información del parqueadero del gestor.
    Responsabilidad: Mostrar información del parqueadero asignado al gestor.
    """
    
    def __init__(self, db):
        self.db = db
        self.mensaje_parqueadero_service = MensajeParqueaderoService(db)
        self.mensaje_error_service = MensajeErrorService()
        self.parqueadero_repo = ParqueaderoRepository(db)
        self.gestor_repo = GestorParqueaderoRepository(db)
    
    def ver_informacion_parqueadero(self, user_id: str) -> dict:
        """
        Muestra información del parqueadero del gestor
        
        Returns:
            dict con: {"success": bool, "parqueadero_id": str}
        """
        try:
            gestor = self.gestor_repo.find_by_id(user_id)
            if not gestor:
                self.mensaje_error_service.error_general(user_id, "No estás registrado como gestor")
                return {"success": False}
            
            parqueadero = self.parqueadero_repo.find_by_id(gestor.parqueadero_id)
            if not parqueadero:
                self.mensaje_error_service.error_parqueadero_no_encontrado(user_id)
                return {"success": False}
            
            self.mensaje_parqueadero_service.mostrar_informacion_parqueadero(user_id, parqueadero)
            return {"success": True, "parqueadero_id": str(gestor.parqueadero_id)}
        except Exception as e:
            print(f"Error al ver información del parqueadero: {e}")
            import traceback
            traceback.print_exc()
            self.mensaje_error_service.error_general(user_id, "Error al consultar información")
            return {"success": False}
