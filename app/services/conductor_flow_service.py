"""
Servicio coordinador para flujos de conversación de conductores en WhatsApp.
Versión refactorizada - delega responsabilidades a servicios especializados.
"""
from app.services.conductor.conductor_menu_service import ConductorMenuService
from app.services.conductor.conductor_parqueadero_service import ConductorParqueaderoService
from app.services.conductor.conductor_suscripcion_service import ConductorSuscripcionService


class ConductorFlowService:
    """
    Servicio coordinador para flujos de conversación de conductores.
    
    Responsabilidades delegadas:
    - ConductorMenuService: Navegación y opciones de menú
    - ConductorParqueaderoService: Consulta y detalles de parqueaderos
    - ConductorSuscripcionService: Gestión de suscripciones y notificaciones
    """
    
    def __init__(self, db):
        self.db = db
        self.menu_service = ConductorMenuService(db)
        self.parqueadero_service = ConductorParqueaderoService(db)
        self.suscripcion_service = ConductorSuscripcionService(db)
    
    # ===== MENÚ PRINCIPAL =====
    
    def mostrar_menu_conductor(self, user_id: str):
        """Muestra el menú principal"""
        self.menu_service.mostrar_menu_conductor(user_id)
    
    def handle_conductor_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú principal"""
        result = self.menu_service.procesar_opcion(text, user_id)
        
        if not result["valid"]:
            self.menu_service.volver_al_menu(user_id)
            return
        
        action = result["action"]
        if action == "ver_parqueaderos":
            self.handle_ver_parqueaderos(user_id)
        elif action == "suscripciones":
            self.handle_mostrar_menu_suscripciones(user_id)
        elif action == "salir":
            self.handle_salir(user_id)
    
    # ===== CONSULTA DE PARQUEADEROS =====
    
    def handle_ver_parqueaderos(self, user_id: str, pagina: int = 1):
        """Muestra parqueaderos con cupos disponibles"""
        result = self.parqueadero_service.consultar_parqueaderos(user_id, pagina)
        
        if result["modo"] == "texto" or result["modo"] == "vacio":
            self.mostrar_menu_conductor(user_id)
    
    def handle_seleccion_parqueadero_detalles(self, text: str, user_id: str):
        """Maneja la selección de un parqueadero para ver detalles"""
        result = self.parqueadero_service.seleccionar_parqueadero_detalles(text, user_id)
        
        action = result.get("action")
        if action == "volver_menu":
            self.mostrar_menu_conductor(user_id)
        elif action == "pagina_anterior" or action == "pagina_siguiente":
            self.handle_ver_parqueaderos(user_id, result.get("pagina", 1))
        elif action == "ver_detalle" or action == "error":
            self.handle_ver_parqueaderos(user_id, result.get("pagina", 1))
    
    # ===== GESTIÓN DE SUSCRIPCIONES =====
    
    def handle_mostrar_menu_suscripciones(self, user_id: str):
        """Muestra el menú de suscripciones"""
        self.suscripcion_service.mostrar_menu_suscripciones(user_id)
    
    def handle_suscripcion_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú de suscripciones"""
        result = self.suscripcion_service.procesar_opcion_menu(text, user_id)
        
        if not result["success"]:
            self.suscripcion_service.mostrar_menu_suscripciones(user_id)
            return
        
        action = result["action"]
        if action == "suscribir_todos":
            result_suscripcion = self.suscripcion_service.suscribir_todos(user_id)
            self.mostrar_menu_conductor(user_id)
        elif action == "suscribir_especifico":
            self.mostrar_parqueaderos_para_suscripcion(user_id)
        elif action == "ver_suscripciones":
            self.mostrar_suscripciones_actuales(user_id)
        elif action == "desuscribir_todos":
            result_suscripcion = self.suscripcion_service.desuscribir_todos(user_id)
            self.mostrar_menu_conductor(user_id)
        elif action == "volver_menu":
            self.mostrar_menu_conductor(user_id)
    
    def mostrar_parqueaderos_para_suscripcion(self, user_id: str):
        """Muestra parqueaderos disponibles para suscripción"""
        self.suscripcion_service.mostrar_parqueaderos_para_suscripcion(user_id)
    
    def handle_seleccion_parqueadero_suscripcion(self, text: str, user_id: str):
        """Maneja la selección de parqueadero para suscripción"""
        result = self.suscripcion_service.seleccionar_parqueadero_suscripcion(text, user_id)
        
        if result["action"] == "volver":
            self.handle_mostrar_menu_suscripciones(user_id)
        else:
            self.mostrar_menu_conductor(user_id)
    
    def mostrar_suscripciones_actuales(self, user_id: str):
        """Muestra las suscripciones actuales del conductor"""
        result = self.suscripcion_service.mostrar_suscripciones_actuales(user_id)
        
        if not result["tiene_suscripciones"] or result["modo"] == "texto":
            self.mostrar_menu_conductor(user_id)
    
    def handle_gestion_suscripciones(self, text: str, user_id: str):
        """Maneja la gestión interactiva de suscripciones (desuscripción)"""
        result = self.suscripcion_service.gestionar_suscripcion(text, user_id)
        
        if result["action"] == "volver":
            self.handle_mostrar_menu_suscripciones(user_id)
        else:
            self.mostrar_menu_conductor(user_id)
    
    def handle_desuscribir_comando(self, text: str, user_id: str):
        """Maneja comandos de desuscripción desde cualquier punto"""
        result = self.suscripcion_service.procesar_comando_desuscripcion(text, user_id)
        
        if result["action"] == "mostrar_ayuda":
            self.handle_mostrar_menu_suscripciones(user_id)
        elif result["action"] == "sin_suscripciones":
            self.handle_mostrar_menu_suscripciones(user_id)
        else:
            self.mostrar_menu_conductor(user_id)
    
    # ===== SALIDA =====
    
    def handle_salir(self, user_id: str):
        """Maneja la salida del usuario"""
        self.menu_service.handle_salir(user_id)
