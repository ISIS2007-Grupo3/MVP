"""
Servicio especializado para navegación del menú de gestores
"""
from app.services.message.mensaje_menu_service import MensajeMenuService
from app.services.message.mensaje_error_service import MensajeErrorService
from app.services.message.mensaje_general_service import MensajeGeneralService
import app.logic.sesion as sesion


class GestorMenuService:
    """
    Servicio enfocado únicamente en la navegación del menú principal de gestores.
    Responsabilidad: Mostrar menú y delegar opciones seleccionadas.
    """
    
    def __init__(self, db):
        self.db = db
        self.mensaje_menu_service = MensajeMenuService(db)
        self.mensaje_error_service = MensajeErrorService()
        self.mensaje_general_service = MensajeGeneralService()
    
    def mostrar_menu_gestor(self, user_id: str):
        """Muestra el menú principal del gestor y actualiza el estado"""
        self.mensaje_menu_service.mostrar_menu_gestor(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_menu", self.db)
    
    def procesar_opcion(self, text: str, user_id: str) -> dict:
        """
        Procesa las opciones del menú de gestor
        
        Returns:
            dict con: {"action": str, "valid": bool}
            action puede ser: "ver_info_parqueadero", "actualizar_cupos", "salir", "invalid"
        """
        if text == "ver_info_parqueadero":
            return {"action": "ver_info_parqueadero", "valid": True}
        elif text == "actualizar_cupos":
            return {"action": "actualizar_cupos", "valid": True}
        elif text == "salir":
            return {"action": "salir", "valid": True}
        else:
            self.mensaje_error_service.error_opcion_invalida_menu_principal(user_id)
            return {"action": "invalid", "valid": False}
    
    def volver_al_menu(self, user_id: str):
        """Muestra el menú principal después de una operación"""
        self.mostrar_menu_gestor(user_id)
    
    def handle_salir(self, user_id: str):
        """Maneja la salida del usuario"""
        self.mensaje_general_service.despedir_usuario(user_id)
        sesion.actualizar_estado_chat(user_id, "inicial", self.db)
