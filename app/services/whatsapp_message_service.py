"""
Servicio coordinador para mensajes de WhatsApp.
Versión refactorizada - delega responsabilidades a servicios especializados.
"""
from app.services.message.mensaje_bienvenida_service import MensajeBienvenidaService
from app.services.message.mensaje_menu_service import MensajeMenuService
from app.services.message.mensaje_error_service import MensajeErrorService
from app.services.message.mensaje_parqueadero_service import MensajeParqueaderoService
from app.services.message.mensaje_suscripcion_service import MensajeSuscripcionService
from app.services.message.mensaje_cupos_service import MensajeCuposService
from app.services.message.mensaje_general_service import MensajeGeneralService
from typing import List


class WhatsAppMessageService:
    """
    Servicio coordinador para mensajes de WhatsApp.
    
    Responsabilidades delegadas:
    - MensajeBienvenidaService: Mensajes de bienvenida y registro
    - MensajeMenuService: Menús interactivos y de texto
    - MensajeErrorService: Mensajes de error y validación
    - MensajeParqueaderoService: Mensajes de parqueaderos
    - MensajeSuscripcionService: Mensajes de suscripciones
    - MensajeCuposService: Mensajes de cupos (gestor)
    - MensajeGeneralService: Mensajes generales del sistema
    """
    
    def __init__(self, db=None):
        self.db = db
        self.bienvenida_service = MensajeBienvenidaService()
        self.menu_service = MensajeMenuService(db)
        self.error_service = MensajeErrorService()
        self.parqueadero_service = MensajeParqueaderoService(db)
        self.suscripcion_service = MensajeSuscripcionService(db)
        self.cupos_service = MensajeCuposService(db)
        self.general_service = MensajeGeneralService()
    
    # ===== MENSAJES DE BIENVENIDA Y REGISTRO =====
    
    def enviar_bienvenida(self, user_id: str):
        """Envía mensaje de bienvenida a nuevos usuarios"""
        self.bienvenida_service.enviar_bienvenida(user_id)
    
    def solicitar_nombre(self, user_id: str):
        """Solicita el nombre para completar el registro"""
        self.bienvenida_service.solicitar_nombre(user_id)
    
    def confirmar_registro(self, user_id: str, nombre: str):
        """Confirma el registro exitoso"""
        self.bienvenida_service.confirmar_registro(user_id, nombre)
    
    def saludar_usuario_registrado(self, user_id: str, nombre: str):
        """Saluda a un usuario ya registrado"""
        self.bienvenida_service.saludar_usuario_registrado(user_id, nombre)
    
    # ===== MENÚS =====
    
    def mostrar_menu_conductor(self, user_id: str):
        """Muestra el menú principal para conductores"""
        self.menu_service.mostrar_menu_conductor(user_id)
    
    def mostrar_menu_suscripciones(self, user_id: str):
        """Muestra el menú de opciones de suscripción"""
        self.menu_service.mostrar_menu_suscripciones(user_id)
    
    def mostrar_menu_gestor(self, user_id: str):
        """Muestra el menú principal para gestores"""
        self.menu_service.mostrar_menu_gestor(user_id)
    
    def solicitar_cupos_actualizacion(self, user_id: str):
        """Solicita información para actualizar cupos"""
        self.menu_service.mostrar_menu_cupos(user_id)
    
    # ===== MENSAJES DE PARQUEADEROS =====
    
    def mostrar_parqueaderos_interactivos(self, user_id: str, parqueaderos: List, pagina: int = 1) -> bool:
        """Muestra lista interactiva de parqueaderos"""
        return self.parqueadero_service.mostrar_parqueaderos_interactivos(user_id, parqueaderos, pagina)
    
    def mostrar_parqueaderos_disponibles(self, user_id: str, parqueaderos: List):
        """Muestra lista de parqueaderos con cupos disponibles"""
        self.parqueadero_service.mostrar_parqueaderos_disponibles(user_id, parqueaderos)
    
    def mostrar_detalle_parqueadero(self, user_id: str, parqueadero):
        """Muestra información detallada de un parqueadero específico"""
        self.parqueadero_service.mostrar_detalle_parqueadero(user_id, parqueadero)
    
    def mostrar_parqueaderos_para_suscripcion(self, user_id: str, parqueaderos: List):
        """Muestra parqueaderos disponibles para suscripción"""
        self.parqueadero_service.mostrar_parqueaderos_para_suscripcion(user_id, parqueaderos)
    
    def mostrar_informacion_parqueadero(self, user_id: str, parqueadero):
        """Muestra información detallada de un parqueadero (vista de gestor)"""
        self.parqueadero_service.mostrar_informacion_parqueadero(user_id, parqueadero)
    
    def mostrar_consultando_parqueaderos(self, user_id: str):
        """Mensaje mientras consulta parqueaderos"""
        self.parqueadero_service.mostrar_consultando_parqueaderos(user_id)
    
    # ===== MENSAJES DE SUSCRIPCIONES =====
    
    def confirmar_suscripcion_global(self, user_id: str):
        """Confirma suscripción a todos los parqueaderos"""
        self.suscripcion_service.confirmar_suscripcion_global(user_id)
    
    def confirmar_suscripcion_especifica(self, user_id: str, nombre_parqueadero: str):
        """Confirma suscripción a un parqueadero específico"""
        self.suscripcion_service.confirmar_suscripcion_especifica(user_id, nombre_parqueadero)
    
    def confirmar_desuscripcion_total(self, user_id: str):
        """Confirma desuscripción de todas las notificaciones"""
        self.suscripcion_service.confirmar_desuscripcion_total(user_id)
    
    def confirmar_desuscripcion_especifica(self, user_id: str, nombre_parqueadero: str):
        """Confirma desuscripción de un parqueadero específico"""
        self.suscripcion_service.confirmar_desuscripcion_especifica(user_id, nombre_parqueadero)
    
    def confirmar_desuscripcion_parqueadero(self, user_id: str, nombre_parqueadero: str):
        """Confirma desuscripción de un parqueadero específico"""
        self.suscripcion_service.confirmar_desuscripcion_parqueadero(user_id, nombre_parqueadero)
    
    def mostrar_suscripciones_actuales(self, user_id: str, suscripciones: List) -> bool:
        """Muestra las suscripciones actuales del conductor"""
        return self.suscripcion_service.mostrar_suscripciones_actuales(user_id, suscripciones)
    
    def mostrar_ayuda_desuscripcion(self, user_id: str, suscripciones: List):
        """Muestra ayuda para comandos de desuscripción"""
        self.suscripcion_service.mostrar_ayuda_desuscripcion(user_id, suscripciones)
    
    def informar_desuscripcion_especifica_limitada(self, user_id: str):
        """Informa sobre limitación de desuscripción específica"""
        self.suscripcion_service.informar_desuscripcion_especifica_limitada(user_id)
    
    def crear_notificacion_cupo_liberado(self, parqueadero) -> str:
        """Crea el mensaje de notificación cuando se libera un cupo"""
        return self.suscripcion_service.crear_notificacion_cupo_liberado(parqueadero)
    
    def enviar_notificacion_cupo(self, user_id: str, mensaje: str):
        """Envía una notificación de cupo liberado"""
        self.suscripcion_service.enviar_notificacion_cupo(user_id, mensaje)
    
    # ===== MENSAJES DE ERROR Y VALIDACIÓN =====
    
    def error_opcion_invalida_menu_principal(self, user_id: str):
        """Error cuando selecciona opción inválida en menú principal"""
        self.error_service.error_opcion_invalida_menu_principal(user_id)
    
    def error_opcion_invalida_suscripciones(self, user_id: str):
        """Error cuando selecciona opción inválida en menú de suscripciones"""
        self.error_service.error_opcion_invalida_suscripciones(user_id)
    
    def error_numero_invalido(self, user_id: str):
        """Error cuando envía un número inválido"""
        self.error_service.error_numero_invalido(user_id)
    
    def error_parqueadero_no_encontrado(self, user_id: str):
        """Error cuando no se encuentra el parqueadero"""
        self.error_service.error_parqueadero_no_encontrado(user_id)
    
    def error_sin_suscripciones(self, user_id: str):
        """Error cuando no tiene suscripciones activas"""
        self.error_service.error_sin_suscripciones(user_id)
    
    def error_suscripcion_general(self, user_id: str, mensaje_error: str):
        """Error general en suscripciones"""
        self.error_service.error_suscripcion_general(user_id, mensaje_error)
    
    def error_rol_no_reconocido(self, user_id: str):
        """Error cuando el rol del usuario no es reconocido"""
        self.error_service.error_rol_no_reconocido(user_id)
    
    def error_formato_cupos(self, user_id: str):
        """Error en formato de actualización de cupos"""
        self.error_service.error_formato_cupos(user_id)
    
    def error_comando_desuscripcion(self, user_id: str):
        """Error en comando de desuscripción"""
        self.error_service.error_comando_desuscripcion(user_id)
    
    def error_confirmacion_cupos(self, user_id: str):
        """Error en la confirmación de cupos"""
        self.error_service.error_confirmacion_cupos(user_id)
    
    # ===== MENSAJES DE ACTUALIZACIÓN DE CUPOS =====
    
    def solicitar_confirmacion_cupos(self, user_id: str, opcion: int, descripcion: str, rango: str):
        """Solicita confirmación antes de actualizar los cupos"""
        self.cupos_service.solicitar_confirmacion_cupos(user_id, opcion, descripcion, rango)
    
    def confirmar_actualizacion_cupos(self, user_id: str, cupos_libres: str, notificaciones_enviadas: int):
        """Confirma la actualización de cupos"""
        self.cupos_service.confirmar_actualizacion_cupos(user_id, cupos_libres, notificaciones_enviadas)
    
    def confirmar_actualizacion_cupos_con_descripcion(self, user_id: str, descripcion: str, cupos_libres: str, notificaciones_enviadas: int):
        """Confirma la actualización de cupos con descripción del estado"""
        self.cupos_service.confirmar_actualizacion_cupos_con_descripcion(user_id, descripcion, cupos_libres, notificaciones_enviadas)
    
    def mostrar_ayuda_cupos(self, user_id: str):
        """Muestra ayuda detallada sobre las opciones de cupos"""
        self.cupos_service.mostrar_ayuda_cupos(user_id)
    
    # ===== MENSAJES DE DESPEDIDA =====
    
    def despedir_usuario(self, user_id: str):
        """Despide al usuario al salir"""
        self.general_service.despedir_usuario(user_id)
