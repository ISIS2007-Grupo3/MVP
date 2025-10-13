"""
Servicio para manejar los flujos de conversación de gestores de parqueadero en WhatsApp
"""
from app.services.whatsapp_message_service import WhatsAppMessageService
from app.services.notification_service import NotificationService
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.repositories.user_repositories import GestorParqueaderoRepository
import app.logic.sesion as sesion


class GestorFlowService:
    """
    Servicio especializado para flujos de conversación de gestores
    Maneja visualización de información del parqueadero y actualización de cupos
    """
    
    def __init__(self, db):
        self.db = db
        self.message_service = WhatsAppMessageService(db)
        self.notification_service = NotificationService(db)
        self.parqueadero_repo = ParqueaderoRepository(db)
        self.gestor_repo = GestorParqueaderoRepository(db)
    
    # ===== MENÚ PRINCIPAL =====
    
    def mostrar_menu_gestor(self, user_id: str):
        """Muestra el menú principal del gestor y actualiza el estado"""
        self.message_service.mostrar_menu_gestor(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_menu", self.db)
    
    def handle_gestor_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú de gestor (texto e interactivo)"""
        # Manejar respuestas de lista interactiva
        if text == "ver_info_parqueadero":
            self.handle_ver_info_parqueadero_gestor(user_id)
        elif text == "actualizar_cupos":
            self.handle_solicitar_actualizacion_cupos(user_id)
        elif text == "salir":
            self.handle_salir(user_id)
        # Mantener compatibilidad con números tradicionales
        elif text == "1":
            self.handle_ver_info_parqueadero_gestor(user_id)
        elif text == "2":
            self.handle_solicitar_actualizacion_cupos(user_id)
        elif text == "3":
            self.handle_salir(user_id)
        else:
            self.message_service.error_opcion_invalida_menu_principal(user_id)
            self.mostrar_menu_gestor(user_id)
    
    # ===== INFORMACIÓN DEL PARQUEADERO =====
    
    def handle_ver_info_parqueadero_gestor(self, user_id: str):
        """Muestra información del parqueadero del gestor"""
        parqueadero_id = self.gestor_repo.obtener_parqueadero_id(user_id)
        
        if not parqueadero_id:
            self.message_service.error_parqueadero_no_encontrado(user_id)
            self.mostrar_menu_gestor(user_id)
            return
            
        parqueadero = self.parqueadero_repo.find_by_id(parqueadero_id)
        if parqueadero:
            self.message_service.mostrar_informacion_parqueadero(user_id, parqueadero)
        else:
            self.message_service.error_parqueadero_no_encontrado(user_id)
        
        self.mostrar_menu_gestor(user_id)
    
    # ===== ACTUALIZACIÓN DE CUPOS =====
    
    def handle_solicitar_actualizacion_cupos(self, user_id: str):
        """Solicita información para actualizar cupos"""
        self.message_service.solicitar_cupos_actualizacion(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_cambio_cupos", self.db)
    
    def handle_cupos_gestor(self, text: str, user_id: str):
        """Procesa la actualización de cupos del gestor usando opciones enumeradas (texto e interactivo)"""
        usuario = sesion.obtener_usuario(user_id, self.db)
        current_step = usuario.estado_chat.paso_actual
        
        # Si está esperando confirmación, manejar esa lógica
        if current_step == "esperando_confirmacion_cupos":
            self.handle_confirmacion_cupos(text, user_id)
            return
        
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
                    self.mostrar_menu_gestor(user_id)
                    return
                    
                opcion, cupos_libres, tiene_cupos, descripcion, rango = opciones_interactivas[text]
                self._solicitar_confirmacion_con_contexto(user_id, opcion, cupos_libres, tiene_cupos, descripcion, rango)
                return
            
            # Manejar comandos especiales
            text_lower = text.strip().lower()
            if text_lower in ['ayuda', 'help', 'info', 'información']:
                self.message_service.mostrar_ayuda_cupos(user_id)
                return
            
            # Manejar entrada de texto tradicional (números)
            opcion = int(text.strip())
            
            # Mapear opciones a valores de cupos con rangos
            opciones_cupos = {
                1: ("0", False, "Parqueadero lleno", "0 cupos"),           
                2: ("3", True, "Pocos cupos disponibles", "1-5 cupos"),      
                3: ("10", True, "Algunos cupos disponibles", "6-15 cupos"),   
                4: ("23", True, "Muchos cupos disponibles", "16-30 cupos"),    
                5: ("35", True, "Parqueadero casi vacío", "30+ cupos"),      
                6: None  # Volver al menú
            }
            
            if opcion == 6:
                # Volver al menú principal
                self.mostrar_menu_gestor(user_id)
                return
            
            if opcion not in opciones_cupos or opciones_cupos[opcion] is None:
                raise ValueError("Opción inválida")
            
            cupos_libres, tiene_cupos, descripcion, rango = opciones_cupos[opcion]
            self._solicitar_confirmacion_con_contexto(user_id, opcion, cupos_libres, tiene_cupos, descripcion, rango)
            
        except (ValueError, IndexError):
            # Si no es un número válido, mostrar el error
            if not text.strip().lower() in ['ayuda', 'help', 'info', 'información']:
                self.message_service.error_formato_cupos(user_id)
                self.message_service.solicitar_cupos_actualizacion(user_id)
        except Exception as e:
            print(f"Error en actualización de cupos: {e}")
            self.message_service.error_suscripcion_general(user_id, "Error al actualizar cupos")
            self.mostrar_menu_gestor(user_id)
    
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
        self.message_service.solicitar_confirmacion_cupos(user_id, opcion, descripcion, rango)
        sesion.actualizar_estado_chat(user_id, "esperando_confirmacion_cupos", self.db)
    
    # ===== CONFIRMACIÓN DE CUPOS =====
    
    def handle_confirmacion_cupos(self, text: str, user_id: str):
        """Maneja la confirmación de la actualización de cupos (texto e interactivo)"""
        try:
            # Manejar respuestas de lista interactiva
            if text == "confirmar_cupos":
                self.ejecutar_actualizacion_cupos(user_id)
                return
            elif text == "reseleccionar_cupos":
                self._reseleccionar_cupos(user_id)
                return
            elif text == "cancelar_cupos":
                self._cancelar_actualizacion(user_id)
                return
            
            # Manejar entrada de texto tradicional (números)
            opcion_confirmacion = int(text.strip())
            
            if opcion_confirmacion == 1:
                # Confirmar actualización
                self.ejecutar_actualizacion_cupos(user_id)
            elif opcion_confirmacion == 2:
                # Volver a seleccionar
                self._reseleccionar_cupos(user_id)
            elif opcion_confirmacion == 3:
                # Cancelar y volver al menú
                self._cancelar_actualizacion(user_id)
            else:
                self._error_confirmacion_y_repreguntar(user_id)
                
        except (ValueError, IndexError):
            self._error_confirmacion_y_repreguntar(user_id)
        except Exception as e:
            print(f"Error en confirmación de cupos: {e}")
            self.message_service.error_suscripcion_general(user_id, "Error en confirmación")
            self.mostrar_menu_gestor(user_id)
    
    def _reseleccionar_cupos(self, user_id: str):
        """Permite al usuario volver a seleccionar el estado del parqueadero"""
        self.message_service.solicitar_cupos_actualizacion(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_cambio_cupos", self.db)
        sesion.actualizar_contexto_temporal(user_id, {}, self.db)
    
    def _cancelar_actualizacion(self, user_id: str):
        """Cancela la actualización y vuelve al menú principal"""
        sesion.actualizar_contexto_temporal(user_id, {}, self.db)
        self.mostrar_menu_gestor(user_id)
    
    def _error_confirmacion_y_repreguntar(self, user_id: str):
        """Muestra error de confirmación y vuelve a preguntar"""
        self.message_service.error_confirmacion_cupos(user_id)
        # Volver a mostrar el menú de confirmación
        usuario = sesion.obtener_usuario(user_id, self.db)
        contexto = usuario.estado_chat.contexto_temporal or {}
        if contexto.get("descripcion") and contexto.get("rango"):
            self.message_service.solicitar_confirmacion_cupos(
                user_id, 
                contexto.get("opcion"), 
                contexto.get("descripcion"), 
                contexto.get("rango")
            )
    
    # ===== EJECUCIÓN DE ACTUALIZACIÓN =====
    
    def ejecutar_actualizacion_cupos(self, user_id: str):
        """Ejecuta la actualización de cupos con los datos confirmados"""
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
            parqueadero_id = self.gestor_repo.obtener_parqueadero_id(user_id)
            if not parqueadero_id:
                self.message_service.error_parqueadero_no_encontrado(user_id)
                self.mostrar_menu_gestor(user_id)
                return
            
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
            self.message_service.confirmar_actualizacion_cupos_con_descripcion(
                user_id, 
                descripcion,
                rango,  # Usar rango en lugar de cupos exactos
                result["notificaciones_enviadas"]
            )
            
            # Limpiar contexto y volver al menú
            sesion.actualizar_contexto_temporal(user_id, {}, self.db)
            self.mostrar_menu_gestor(user_id)
            
        except Exception as e:
            print(f"Error ejecutando actualización: {e}")
            self.message_service.error_suscripcion_general(user_id, "Error al actualizar cupos")
            self.mostrar_menu_gestor(user_id)
    
    # ===== SALIDA =====
    
    def handle_salir(self, user_id: str):
        """Maneja la salida del usuario"""
        self.message_service.despedir_usuario(user_id)
        sesion.actualizar_estado_chat(user_id, "inicial", self.db)
