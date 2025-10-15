"""
Servicio coordinador para flujos de conversación de gestores en WhatsApp.
Versión refactorizada - delega responsabilidades a servicios especializados.
"""
from app.services.gestor.gestor_menu_service import GestorMenuService
from app.services.gestor.gestor_parqueadero_service import GestorParqueaderoService
from app.services.gestor.gestor_cupos_service import GestorCuposService


class GestorFlowService:
    """
    Servicio coordinador para flujos de conversación de gestores.
    
    Responsabilidades delegadas:
    - GestorMenuService: Navegación y opciones de menú
    - GestorParqueaderoService: Información del parqueadero
    - GestorCuposService: Actualización de cupos y notificaciones
    """
    
    def __init__(self, db):
        self.db = db
        self.menu_service = GestorMenuService(db)
        self.parqueadero_service = GestorParqueaderoService(db)
        self.cupos_service = GestorCuposService(db)
    
    # ===== MENÚ PRINCIPAL =====
    
    def mostrar_menu_gestor(self, user_id: str):
        """Muestra el menú principal del gestor"""
        self.menu_service.mostrar_menu_gestor(user_id)
    
    def handle_gestor_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú de gestor"""
        result = self.menu_service.procesar_opcion(text, user_id)
        
        if not result["valid"]:
            self.menu_service.volver_al_menu(user_id)
            return
        
        action = result["action"]
        if action == "ver_info_parqueadero":
            self.handle_ver_info_parqueadero_gestor(user_id)
        elif action == "actualizar_cupos":
            self.handle_solicitar_actualizacion_cupos(user_id)
        elif action == "salir":
            self.handle_salir(user_id)
    
    # ===== INFORMACIÓN DEL PARQUEADERO =====
    
    def handle_ver_info_parqueadero_gestor(self, user_id: str):
        """Muestra información del parqueadero del gestor"""
        self.parqueadero_service.ver_informacion_parqueadero(user_id)
        self.mostrar_menu_gestor(user_id)
    
    # ===== ACTUALIZACIÓN DE CUPOS =====
    
    def handle_solicitar_actualizacion_cupos(self, user_id: str):
        """Solicita información para actualizar cupos"""
        self.cupos_service.solicitar_actualizacion_cupos(user_id)
    
    def handle_cupos_gestor(self, text: str, user_id: str):
        """Procesa la actualización de cupos del gestor"""
        result = self.cupos_service.procesar_actualizacion_cupos(text, user_id)
        
        action = result.get("action")
        if action == "volver_menu":
            self.mostrar_menu_gestor(user_id)
        elif action == "error":
            # El servicio ya mostró el error, no hacer nada adicional
            pass
        # Si action == "confirmacion" o "ayuda", el flujo continúa en el servicio
    
    def handle_confirmacion_cupos(self, text: str, user_id: str):
        """Maneja la confirmación de la actualización de cupos"""
        result = self.cupos_service.procesar_confirmacion_cupos(text, user_id)
        
        # El servicio de cupos ahora maneja mostrar el menú después de actualizar/cancelar
        # No se necesita hacer nada adicional aquí
        action = result.get("action")
        if action == "error":
            # El servicio ya mostró el error y volvió a preguntar
            pass
        # Para "actualizar", "cancelar" y "reseleccionar", el servicio maneja el flujo
    
    # ===== SALIDA =====
    
    def handle_salir(self, user_id: str):
        """Maneja la salida del usuario"""
        self.menu_service.handle_salir(user_id)
