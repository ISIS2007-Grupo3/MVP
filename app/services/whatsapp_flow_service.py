"""
Servicio coordinador para manejar los flujos de conversación de WhatsApp.
Delega a servicios especializados según el rol del usuario (Conductor o Gestor).
"""
from app.services.conductor_flow_service import ConductorFlowService
from app.services.gestor_flow_service import GestorFlowService


class WhatsAppFlowService:
    """
    Servicio coordinador de flujos de conversación de WhatsApp.
    Delega a servicios especializados según el rol del usuario.
    """
    
    def __init__(self, db):
        self.db = db
        self.conductor_service = ConductorFlowService(db)
        self.gestor_service = GestorFlowService(db)
    
    # ===== MÉTODOS DE CONDUCTOR (Delegación) =====
    
    def handle_conductor_menu_option(self, text: str, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_conductor_menu_option(text, user_id)
    
    def handle_ver_parqueaderos(self, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_ver_parqueaderos(user_id)
    
    def handle_mostrar_menu_suscripciones(self, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_mostrar_menu_suscripciones(user_id)
    
    def handle_suscripcion_menu_option(self, text: str, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_suscripcion_menu_option(text, user_id)
    
    def handle_seleccion_parqueadero_suscripcion(self, text: str, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_seleccion_parqueadero_suscripcion(text, user_id)
    
    def mostrar_suscripciones_actuales(self, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.mostrar_suscripciones_actuales(user_id)
    
    def handle_desuscribir_comando(self, text: str, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_desuscribir_comando(text, user_id)
    
    def mostrar_menu_conductor(self, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.mostrar_menu_conductor(user_id)
    
    def handle_seleccion_parqueadero_detalles(self, text: str, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_seleccion_parqueadero_detalles(text, user_id)
    
    def handle_gestion_suscripciones(self, text: str, user_id: str):
        """Delega al servicio de conductor"""
        return self.conductor_service.handle_gestion_suscripciones(text, user_id)
    
    # ===== MÉTODOS DE GESTOR (Delegación) =====
    
    def handle_gestor_menu_option(self, text: str, user_id: str):
        """Delega al servicio de gestor"""
        return self.gestor_service.handle_gestor_menu_option(text, user_id)
    
    def handle_ver_info_parqueadero_gestor(self, user_id: str):
        """Delega al servicio de gestor"""
        return self.gestor_service.handle_ver_info_parqueadero_gestor(user_id)
    
    def handle_solicitar_actualizacion_cupos(self, user_id: str):
        """Delega al servicio de gestor"""
        return self.gestor_service.handle_solicitar_actualizacion_cupos(user_id)
    
    def handle_cupos_gestor(self, text: str, user_id: str):
        """Delega al servicio de gestor"""
        return self.gestor_service.handle_cupos_gestor(text, user_id)
    
    def handle_confirmacion_cupos(self, text: str, user_id: str):
        """Delega al servicio de gestor"""
        return self.gestor_service.handle_confirmacion_cupos(text, user_id)
    
    def mostrar_menu_gestor(self, user_id: str):
        """Delega al servicio de gestor"""
        return self.gestor_service.mostrar_menu_gestor(user_id)
    
    # ===== MÉTODOS COMPARTIDOS =====
    
    def handle_salir(self, user_id: str):
        """
        Maneja la salida del usuario.
        Puede ser usado tanto por conductores como por gestores.
        """
        return self.conductor_service.handle_salir(user_id)
