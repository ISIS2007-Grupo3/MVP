"""
Servicio especializado para gestión de cupos (gestor)
"""
from app.services.message.mensaje_menu_service import MensajeMenuService
from app.services.message.mensaje_cupos_service import MensajeCuposService
from app.services.message.mensaje_error_service import MensajeErrorService
from app.services.notification_service import NotificationService
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.repositories.user_repositories import GestorParqueaderoRepository
import app.logic.sesion as sesion


class GestorCuposService:
    """
    Servicio enfocado en la actualización de cupos del parqueadero.
    Responsabilidad: Procesar actualizaciones de disponibilidad y notificar conductores.
    """
    
    def __init__(self, db):
        self.db = db
        self.mensaje_menu_service = MensajeMenuService(db)
        self.mensaje_cupos_service = MensajeCuposService(db)
        self.mensaje_error_service = MensajeErrorService()
        self.notification_service = NotificationService(db)
        self.parqueadero_repo = ParqueaderoRepository(db)
        self.gestor_repo = GestorParqueaderoRepository(db)
    
    def solicitar_actualizacion_cupos(self, user_id: str):
        """Solicita información para actualizar cupos"""
        self.mensaje_menu_service.mostrar_menu_cupos(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_cambio_cupos", self.db)
    
    def procesar_actualizacion_cupos(self, text: str, user_id: str) -> dict:
        """
        Procesa la actualización de cupos del gestor usando opciones enumeradas
        
        Returns:
            dict con: {"action": str, "success": bool}
            action puede ser: "confirmacion", "volver_menu", "ayuda", "error"
        """
        usuario = sesion.obtener_usuario(user_id, self.db)
        current_step = usuario.estado_chat.paso_actual
        
        # Si está esperando confirmación, delegar a método de confirmación
        if current_step == "esperando_confirmacion_cupos":
            return self.procesar_confirmacion_cupos(text, user_id)
        
        try:
            # Manejar respuestas de lista interactiva
            opciones_interactivas = {
                "cupos_lleno": (1, "0", False, "Parqueadero lleno", "0 cupos"),
                "cupos_pocos": (2, "3", True, "Pocos cupos disponibles", "1-5 cupos"),
                "cupos_algunos": (3, "10", True, "Algunos cupos disponibles", "6-15 cupos"),
                "cupos_muchos": (4, "23", True, "Muchos cupos disponibles", "16-30 cupos"),
                "cupos_casi_vacio": (5, "35", True, "Parqueadero casi vacío", "30+ cupos"),
                "volver_menu_gestor": None
            }
            
            if text in opciones_interactivas:
                if text == "volver_menu_gestor":
                    return {"action": "volver_menu", "success": True}
                    
                opcion, cupos_libres, tiene_cupos, descripcion, rango = opciones_interactivas[text]
                self._solicitar_confirmacion_con_contexto(user_id, opcion, cupos_libres, tiene_cupos, descripcion, rango)
                return {"action": "confirmacion", "success": True}
            
            # Manejar comandos especiales
            text_lower = text.strip().lower()
            if text_lower in ['ayuda', 'help', 'info', 'información']:
                self.mensaje_cupos_service.mostrar_ayuda_cupos(user_id)
                return {"action": "ayuda", "success": True}
            
            # Si no coincide con ninguna opción conocida
            self.mensaje_error_service.error_formato_cupos(user_id)
            self.mensaje_menu_service.mostrar_menu_cupos(user_id)
            return {"action": "error", "success": False}
        except Exception as e:
            print(f"Error en actualización de cupos: {e}")
            self.mensaje_error_service.error_suscripcion_general(user_id, "Error al actualizar cupos")
            return {"action": "error", "success": False}
    
    def _solicitar_confirmacion_con_contexto(self, user_id: str, opcion: int, cupos_libres: str, 
                                              tiene_cupos: bool, descripcion: str, rango: str):
        """Guarda el contexto y solicita confirmación de la actualización"""
        # Guardar datos en contexto temporal y solicitar confirmación
        contexto = {
            "opcion": opcion,
            "cupos_libres": cupos_libres,
            "tiene_cupos": tiene_cupos,
            "descripcion": descripcion,
            "rango": rango
        }
        sesion.actualizar_contexto_temporal(user_id, contexto, self.db)
        
        # Mostrar mensaje de confirmación
        self.mensaje_cupos_service.solicitar_confirmacion_cupos(user_id, opcion, descripcion, rango)
        sesion.actualizar_estado_chat(user_id, "esperando_confirmacion_cupos", self.db)
    
    def procesar_confirmacion_cupos(self, text: str, user_id: str) -> dict:
        """
        Maneja la confirmación de la actualización de cupos
        
        Returns:
            dict con: {"action": str, "success": bool}
            action puede ser: "actualizar", "reseleccionar", "cancelar", "error"
        """
        try:
            # Manejar respuestas de lista interactiva
            if text == "confirmar_cupos":
                self.ejecutar_actualizacion_cupos(user_id)
                return {"action": "actualizar", "success": True}
            elif text == "reseleccionar_cupos":
                self._reseleccionar_cupos(user_id)
                return {"action": "reseleccionar", "success": True}
            elif text == "cancelar_cupos":
                self._cancelar_actualizacion(user_id)
                return {"action": "cancelar", "success": True}
            else:
                self._error_confirmacion_y_repreguntar(user_id)
                return {"action": "error", "success": False}
                
        except Exception as e:
            print(f"Error en confirmación de cupos: {e}")
            self.mensaje_error_service.error_suscripcion_general(user_id, "Error en confirmación")
            return {"action": "error", "success": False}
    
    def _reseleccionar_cupos(self, user_id: str):
        """Permite al usuario volver a seleccionar el estado del parqueadero"""
        self.mensaje_menu_service.mostrar_menu_cupos(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_cambio_cupos", self.db)
        sesion.actualizar_contexto_temporal(user_id, {}, self.db)
    
    def _cancelar_actualizacion(self, user_id: str):
        """Cancela la actualización y vuelve al menú principal"""
        sesion.actualizar_contexto_temporal(user_id, {}, self.db)
    
    def _error_confirmacion_y_repreguntar(self, user_id: str):
        """Muestra error de confirmación y vuelve a preguntar"""
        self.mensaje_error_service.error_confirmacion_cupos(user_id)
        # Volver a mostrar el menú de confirmación
        usuario = sesion.obtener_usuario(user_id, self.db)
        contexto = usuario.estado_chat.contexto_temporal or {}
        if contexto.get("descripcion") and contexto.get("rango"):
            self.mensaje_cupos_service.solicitar_confirmacion_cupos(
                user_id, 
                contexto.get("opcion"), 
                contexto.get("descripcion"), 
                contexto.get("rango")
            )
    
    def ejecutar_actualizacion_cupos(self, user_id: str) -> dict:
        """
        Ejecuta la actualización de cupos con los datos confirmados
        
        Returns:
            dict con: {"success": bool, "notificaciones_enviadas": int}
        """
        try:
            # Obtener datos del contexto temporal
            usuario = sesion.obtener_usuario(user_id, self.db)
            contexto = usuario.estado_chat.contexto_temporal or {}
            
            cupos_libres = contexto.get("cupos_libres")
            tiene_cupos = contexto.get("tiene_cupos")
            descripcion = contexto.get("descripcion")
            rango = contexto.get("rango")
            
            if not all([cupos_libres is not None, tiene_cupos is not None, descripcion, rango]):
                raise ValueError("Datos incompletos en contexto")
            
            # Obtener parqueadero del gestor
            gestor = self.gestor_repo.find_by_id(usuario.id)
            if not gestor:
                self.mensaje_error_service.error_parqueadero_no_encontrado(user_id)
                return {"success": False, "notificaciones_enviadas": 0}
            
            parqueadero_id = gestor.parqueadero_id
            
            # Actualizar cupos con rango y enviar notificaciones
            result = self.parqueadero_repo.actualizar_cupos_con_notificacion(
                parqueadero_id, 
                cupos_libres, 
                tiene_cupos,
                rango,
                descripcion,
                self.notification_service
            )
            
            # Mostrar confirmación personalizada
            self.mensaje_cupos_service.confirmar_actualizacion_cupos_con_descripcion(
                user_id, 
                descripcion,
                rango,
                result["notificaciones_enviadas"]
            )
            
            # Limpiar contexto
            sesion.actualizar_contexto_temporal(user_id, {}, self.db)
            
            return {
                "success": True, 
                "notificaciones_enviadas": result["notificaciones_enviadas"]
            }
            
        except Exception as e:
            print(f"Error ejecutando actualización: {e}")
            self.mensaje_error_service.error_suscripcion_general(user_id, "Error al actualizar cupos")
            return {"success": False, "notificaciones_enviadas": 0}
