"""
Servicio especializado para gestión de suscripciones de conductores
"""
from app.services.message.mensaje_menu_service import MensajeMenuService
from app.services.message.mensaje_suscripcion_service import MensajeSuscripcionService
from app.services.message.mensaje_parqueadero_service import MensajeParqueaderoService
from app.services.message.mensaje_error_service import MensajeErrorService
from app.services.notification_service import NotificationService
from app.repositories.parqueadero_repository import ParqueaderoRepository
import app.logic.sesion as sesion


class ConductorSuscripcionService:
    """
    Servicio enfocado en gestión de suscripciones de conductores.
    Responsabilidad: Suscribir, desuscribir y listar suscripciones.
    """
    
    def __init__(self, db):
        self.db = db
        self.mensaje_menu_service = MensajeMenuService(db)
        self.mensaje_suscripcion_service = MensajeSuscripcionService(db)
        self.mensaje_parqueadero_service = MensajeParqueaderoService(db)
        self.mensaje_error_service = MensajeErrorService()
        self.notification_service = NotificationService(db)
        self.parqueadero_repo = ParqueaderoRepository(db)
    
    def mostrar_menu_suscripciones(self, user_id: str):
        """Muestra el menú de suscripciones"""
        self.mensaje_menu_service.mostrar_menu_suscripciones(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_suscripcion", self.db)
    
    def procesar_opcion_menu(self, text: str, user_id: str) -> dict:
        """
        Procesa las opciones del menú de suscripciones
        
        Returns:
            dict con: {"action": str, "success": bool}
            action puede ser: "suscribir_todos", "suscribir_especifico", "ver_suscripciones", "desuscribir_todos", "volver_menu", "invalid"
        """
        if text == "suscribir_todos":
            return {"action": "suscribir_todos", "success": True}
        elif text == "suscribir_especifico":
            return {"action": "suscribir_especifico", "success": True}
        elif text == "ver_suscripciones":
            return {"action": "ver_suscripciones", "success": True}
        elif text == "desuscribir_todos":
            return {"action": "desuscribir_todos", "success": True}
        elif text == "volver_menu":
            return {"action": "volver_menu", "success": True}
        else:
            self.mensaje_error_service.error_opcion_invalida_suscripciones(user_id)
            return {"action": "invalid", "success": False}
    
    def suscribir_todos(self, user_id: str) -> dict:
        """Suscribe al conductor a todos los parqueaderos"""
        result = self.notification_service.suscribir_conductor(user_id, None)
        if not result["success"]:
            self.mensaje_error_service.error_suscripcion_general(user_id, result["message"])
        return result
    
    def desuscribir_todos(self, user_id: str) -> dict:
        """Desuscribe al conductor de todos los parqueaderos"""
        result = self.notification_service.desuscribir_conductor(user_id, None)
        if not result["success"]:
            self.mensaje_error_service.error_suscripcion_general(user_id, result["message"])
        return result
    
    def mostrar_parqueaderos_para_suscripcion(self, user_id: str):
        """Muestra los parqueaderos disponibles para suscripción"""
        try:
            parqueaderos = self.parqueadero_repo.find_all()
            print(f"Debug: Parqueaderos encontrados: {len(parqueaderos)}")
            
            if parqueaderos:
                self.mensaje_parqueadero_service.mostrar_parqueaderos_para_suscripcion(user_id, parqueaderos)
                # Guardar lista de parqueaderos en sesión para referencia
                parqueaderos_ids = [p.id for p in parqueaderos]
                print(f"Debug: IDs de parqueaderos guardados: {parqueaderos_ids}")
                
                sesion.actualizar_contexto_temporal(user_id, {"parqueaderos": parqueaderos_ids}, self.db)
                sesion.actualizar_estado_chat(user_id, "esperando_seleccion_parqueadero", self.db)
            else:
                self.mensaje_parqueadero_service.mostrar_parqueaderos_para_suscripcion(user_id, [])
        except Exception as e:
            print(f"Error en mostrar_parqueaderos_para_suscripcion: {e}")
            self.mensaje_error_service.error_suscripcion_general(user_id, "Error al cargar parqueaderos")
    
    def seleccionar_parqueadero_suscripcion(self, text: str, user_id: str) -> dict:
        """
        Maneja la selección de parqueadero para suscripción
        
        Returns:
            dict con: {"action": str, "success": bool, "parqueadero_id": str}
        """
        try:
            # Manejar respuestas de lista interactiva
            if text == "volver_suscripciones":
                return {"action": "volver", "success": True}
                
            if text.startswith("parqueadero_"):
                # Extraer índice del ID del parqueadero
                index = int(text.split("_")[1])
                usuario = sesion.obtener_usuario(user_id, self.db)
                contexto_temporal = usuario.estado_chat.contexto_temporal or {}
                parqueaderos_ids = contexto_temporal.get('parqueaderos', [])
                
                if 0 <= index < len(parqueaderos_ids):
                    parqueadero_id = parqueaderos_ids[index]
                    result = self.notification_service.suscribir_conductor(user_id, parqueadero_id)
                    
                    if not result["success"]:
                        self.mensaje_error_service.error_suscripcion_general(user_id, result["message"])
                    else:
                        # Limpiar contexto temporal después de suscripción exitosa
                        sesion.actualizar_contexto_temporal(user_id, {}, self.db)
                    
                    return {"action": "suscripcion", "success": result["success"], "parqueadero_id": parqueadero_id}
                else:
                    self.mensaje_error_service.error_numero_invalido(user_id)
                    return {"action": "error", "success": False}
                
        except ValueError as e:
            print(f"Debug: Error de valor: {e}")
            self.mensaje_error_service.error_numero_invalido(user_id)
            return {"action": "error", "success": False}
        except Exception as e:
            print(f"Error en selección de parqueadero: {e}")
            import traceback
            traceback.print_exc()
            self.mensaje_error_service.error_suscripcion_general(user_id, "Error interno del sistema")
            return {"action": "error", "success": False}
    
    def mostrar_suscripciones_actuales(self, user_id: str) -> dict:
        """
        Muestra las suscripciones actuales del conductor
        
        Returns:
            dict con: {"tiene_suscripciones": bool, "modo": str}
        """
        suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
        
        if not suscripciones:
            self.mensaje_suscripcion_service.mostrar_suscripciones_actuales(user_id, suscripciones)
            return {"tiene_suscripciones": False, "modo": "vacio"}
        
        # Mostrar menú interactivo y cambiar estado si fue exitoso
        success = self.mensaje_suscripcion_service.mostrar_suscripciones_actuales(user_id, suscripciones)
        if success:
            # Guardar suscripciones en contexto para manejar desuscripción
            sesion.actualizar_contexto_temporal(user_id, {"suscripciones": suscripciones}, self.db)
            sesion.actualizar_estado_chat(user_id, "gestionando_suscripciones", self.db)
            return {"tiene_suscripciones": True, "modo": "interactivo"}
        else:
            return {"tiene_suscripciones": True, "modo": "texto"}
    
    def gestionar_suscripcion(self, text: str, user_id: str) -> dict:
        """
        Maneja la gestión interactiva de suscripciones (desuscripción)
        
        Returns:
            dict con: {"action": str, "success": bool}
        """
        try:
            # Obtener contexto
            usuario = sesion.obtener_usuario(user_id, self.db)
            contexto_temporal = usuario.estado_chat.contexto_temporal or {}
            suscripciones = contexto_temporal.get('suscripciones', [])
            
            # Manejar opción de volver
            if text == "volver_suscripciones":
                return {"action": "volver", "success": True}
            
            # Manejar desuscribir todo
            if text == "desuscribir_todo":
                result = self.notification_service.desuscribir_conductor(user_id, None)
                if result["success"]:
                    self.mensaje_suscripcion_service.confirmar_desuscripcion_total(user_id)
                else:
                    self.mensaje_error_service.error_suscripcion_general(user_id, result["message"])
                return {"action": "desuscribir_todo", "success": result["success"]}
            
            # Manejar desuscripción individual
            if text.startswith("desuscribir_"):
                try:
                    index = int(text.split("_")[1])
                    
                    if 0 <= index < len(suscripciones):
                        suscripcion = suscripciones[index]
                        
                        if suscripcion["tipo"] == "global":
                            # Desuscribir de todos
                            result = self.notification_service.desuscribir_conductor(user_id, None)
                            if result["success"]:
                                self.mensaje_suscripcion_service.confirmar_desuscripcion_total(user_id)
                            else:
                                self.mensaje_error_service.error_suscripcion_general(user_id, result["message"])
                        else:
                            # Desuscribir de parqueadero específico
                            parqueadero_id = suscripcion.get("parqueadero_id")
                            if parqueadero_id:
                                result = self.notification_service.desuscribir_conductor(user_id, parqueadero_id)
                                if result["success"]:
                                    self.mensaje_suscripcion_service.confirmar_desuscripcion_parqueadero(user_id, suscripcion['parqueadero'])
                                else:
                                    self.mensaje_error_service.error_suscripcion_general(user_id, result["message"])
                            else:
                                self.mensaje_error_service.error_suscripcion_general(user_id, "No se pudo identificar el parqueadero")
                                return {"action": "error", "success": False}
                        
                        return {"action": "desuscribir_individual", "success": True}
                    else:
                        self.mensaje_error_service.error_numero_invalido(user_id)
                        return {"action": "error", "success": False}
                        
                except (ValueError, IndexError) as e:
                    print(f"Error procesando desuscripción: {e}")
                    self.mensaje_error_service.error_numero_invalido(user_id)
                    return {"action": "error", "success": False}
            
            # Opción no reconocida
            self.mensaje_error_service.error_opcion_invalida(user_id)
            return {"action": "invalid", "success": False}
            
        except Exception as e:
            print(f"Error en gestión de suscripciones: {e}")
            import traceback
            traceback.print_exc()
            self.mensaje_error_service.error_suscripcion_general(user_id, "Error al procesar la solicitud")
            return {"action": "error", "success": False}
    
    def procesar_comando_desuscripcion(self, text: str, user_id: str) -> dict:
        """
        Maneja comandos de desuscripción desde cualquier punto de la conversación
        
        Returns:
            dict con: {"action": str, "success": bool}
        """
        comando_parts = text.lower().split()
        
        if len(comando_parts) == 1:  # Solo "desuscribir"
            suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
            
            if not suscripciones:
                self.mensaje_error_service.error_sin_suscripciones(user_id)
                return {"action": "sin_suscripciones", "success": False}
                
            self.mensaje_suscripcion_service.mostrar_ayuda_desuscripcion(user_id, suscripciones)
            return {"action": "mostrar_ayuda", "success": True}
            
        elif len(comando_parts) == 2:
            if comando_parts[1] == "todo":
                # Desuscribir de todo
                result = self.notification_service.desuscribir_conductor(user_id, None)
                return {"action": "desuscribir_todo", "success": result["success"]}
            else:
                try:
                    # Desuscribir de suscripción específica por número
                    numero = int(comando_parts[1])
                    suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
                    
                    if 1 <= numero <= len(suscripciones):
                        suscripcion = suscripciones[numero - 1]
                        if suscripcion["tipo"] == "global":
                            result = self.notification_service.desuscribir_conductor(user_id, None)
                            return {"action": "desuscribir_global", "success": result["success"]}
                        else:
                            self.mensaje_suscripcion_service.informar_desuscripcion_especifica_limitada(user_id)
                            return {"action": "limitado", "success": False}
                    else:
                        self.mensaje_error_service.error_numero_invalido(user_id)
                        return {"action": "error", "success": False}
                except ValueError:
                    self.mensaje_error_service.error_comando_desuscripcion(user_id)
                    return {"action": "error", "success": False}
        else:
            self.mensaje_error_service.error_comando_desuscripcion(user_id)
            return {"action": "error", "success": False}
