from app.services.whatsapp_message_service import WhatsAppMessageService
from app.services.notification_service import NotificationService
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.repositories.user_repositories import GestorParqueaderoRepository
from app.logic.parqueaderos import obtener_parqueaderos_con_cupos
import app.logic.sesion as sesion

class WhatsAppFlowService:
    """
    Servicio para manejar los flujos de conversación de WhatsApp
    Separado de la lógica de mensajes para mayor claridad
    """
    
    def __init__(self, db):
        self.db = db
        self.message_service = WhatsAppMessageService(db)
        self.notification_service = NotificationService(db)
        self.parqueadero_repo = ParqueaderoRepository(db)
        self.gestor_repo = GestorParqueaderoRepository(db)
    
    # ===== FLUJOS DE CONDUCTOR =====
    
    def handle_conductor_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú principal de conductor"""
        if text == "1":
            self.handle_ver_parqueaderos(user_id)
        elif text == "2":
            self.handle_mostrar_menu_suscripciones(user_id)
        elif text == "3":
            self.handle_salir(user_id)
        else:
            self.message_service.error_opcion_invalida_menu_principal(user_id)
            self.mostrar_menu_conductor(user_id)
    
    def handle_ver_parqueaderos(self, user_id: str):
        """Maneja la consulta de parqueaderos disponibles"""
        self.message_service.mostrar_consultando_parqueaderos(user_id)
        parqueaderos = obtener_parqueaderos_con_cupos(self.db)
        self.message_service.mostrar_parqueaderos_disponibles(user_id, parqueaderos)
        self.mostrar_menu_conductor(user_id)
    
    def handle_mostrar_menu_suscripciones(self, user_id: str):
        """Muestra el menú de suscripciones"""
        self.message_service.mostrar_menu_suscripciones(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_suscripcion", self.db)
    
    def handle_suscripcion_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú de suscripciones"""
        if text == "1":
            # Suscribirse a todos los parqueaderos
            result = self.notification_service.suscribir_conductor(user_id, None)
            if not result["success"]:
                self.message_service.error_suscripcion_general(user_id, result["message"])
            self.mostrar_menu_conductor(user_id)
            
        elif text == "2":
            # Mostrar parqueaderos para suscripción específica
            self.mostrar_parqueaderos_para_suscripcion(user_id)
            
        elif text == "3":
            # Ver suscripciones actuales
            self.mostrar_suscripciones_actuales(user_id)
            
        elif text == "4":
            # Desuscribirse de todas
            result = self.notification_service.desuscribir_conductor(user_id, None)
            if not result["success"]:
                self.message_service.error_suscripcion_general(user_id, result["message"])
            self.mostrar_menu_conductor(user_id)
            
        elif text == "5":
            # Volver al menú principal
            self.mostrar_menu_conductor(user_id)
            
        else:
            self.message_service.error_opcion_invalida_suscripciones(user_id)
            self.handle_mostrar_menu_suscripciones(user_id)
    
    def mostrar_parqueaderos_para_suscripcion(self, user_id: str):
        """Muestra los parqueaderos disponibles para suscripción"""
        try:
            parqueaderos = self.parqueadero_repo.find_all()
            print(f"Debug: Parqueaderos encontrados: {len(parqueaderos)}")
            
            if parqueaderos:
                self.message_service.mostrar_parqueaderos_para_suscripcion(user_id, parqueaderos)
                # Guardar lista de parqueaderos en sesión para referencia
                parqueaderos_ids = [p.id for p in parqueaderos]
                print(f"Debug: IDs de parqueaderos guardados: {parqueaderos_ids}")
                
                sesion.actualizar_contexto_temporal(user_id, {"parqueaderos": parqueaderos_ids}, self.db)
                sesion.actualizar_estado_chat(user_id, "esperando_seleccion_parqueadero", self.db)
            else:
                self.message_service.mostrar_parqueaderos_para_suscripcion(user_id, [])
                self.handle_mostrar_menu_suscripciones(user_id)
        except Exception as e:
            print(f"Error en mostrar_parqueaderos_para_suscripcion: {e}")
            self.message_service.error_suscripcion_general(user_id, "Error al cargar parqueaderos")
            self.handle_mostrar_menu_suscripciones(user_id)
    
    def handle_seleccion_parqueadero_suscripcion(self, text: str, user_id: str):
        """Maneja la selección de parqueadero para suscripción"""
        try:
            opcion = int(text)
            usuario = sesion.obtener_usuario(user_id, self.db)
            print(f"Debug: Usuario obtenido: {usuario.id if usuario else 'None'}")
            
            # Acceder correctamente al contexto temporal
            contexto_temporal = usuario.estado_chat.contexto_temporal or {}
            parqueaderos_ids = contexto_temporal.get('parqueaderos', [])
            print(f"Debug: Contexto temporal: {contexto_temporal}")
            print(f"Debug: Parqueaderos IDs disponibles: {parqueaderos_ids}")
            print(f"Debug: Opción seleccionada: {opcion}")
            
            if opcion == len(parqueaderos_ids) + 1:
                # Volver al menú de suscripciones
                print("Debug: Usuario eligió volver al menú")
                self.handle_mostrar_menu_suscripciones(user_id)
                return
                
            if 1 <= opcion <= len(parqueaderos_ids):
                parqueadero_id = parqueaderos_ids[opcion - 1]
                print(f"Debug: ID del parqueadero seleccionado: {parqueadero_id}")
                
                result = self.notification_service.suscribir_conductor(user_id, parqueadero_id)
                print(f"Debug: Resultado de suscripción: {result}")
                
                if not result["success"]:
                    self.message_service.error_suscripcion_general(user_id, result["message"])
                else:
                    # Limpiar contexto temporal después de suscripción exitosa
                    sesion.actualizar_contexto_temporal(user_id, {}, self.db)
            else:
                print(f"Debug: Opción fuera de rango. Opciones válidas: 1-{len(parqueaderos_ids)}")
                self.message_service.error_numero_invalido(user_id)
                
        except ValueError as e:
            print(f"Debug: Error de valor: {e}")
            self.message_service.error_numero_invalido(user_id)
        except Exception as e:
            print(f"Error en selección de parqueadero: {e}")
            import traceback
            traceback.print_exc()
            self.message_service.error_suscripcion_general(user_id, "Error interno del sistema")
        
        self.mostrar_menu_conductor(user_id)
    
    def mostrar_suscripciones_actuales(self, user_id: str):
        """Muestra las suscripciones actuales del conductor"""
        suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
        self.message_service.mostrar_suscripciones_actuales(user_id, suscripciones)
        self.mostrar_menu_conductor(user_id)
    
    def handle_desuscribir_comando(self, text: str, user_id: str):
        """Maneja comandos de desuscripción desde cualquier punto de la conversación"""
        comando_parts = text.lower().split()
        
        if len(comando_parts) == 1:  # Solo "desuscribir"
            suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
            
            if not suscripciones:
                self.message_service.error_sin_suscripciones(user_id)
                return
                
            self.message_service.mostrar_ayuda_desuscripcion(user_id, suscripciones)
            
        elif len(comando_parts) == 2:
            if comando_parts[1] == "todo":
                # Desuscribir de todo
                self.notification_service.desuscribir_conductor(user_id, None)
            else:
                try:
                    # Desuscribir de suscripción específica por número
                    numero = int(comando_parts[1])
                    suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
                    
                    if 1 <= numero <= len(suscripciones):
                        suscripcion = suscripciones[numero - 1]
                        if suscripcion["tipo"] == "global":
                            self.notification_service.desuscribir_conductor(user_id, None)
                        else:
                            self.message_service.informar_desuscripcion_especifica_limitada(user_id)
                    else:
                        self.message_service.error_numero_invalido(user_id)
                except ValueError:
                    self.message_service.error_comando_desuscripcion(user_id)
        else:
            self.message_service.error_comando_desuscripcion(user_id)
    
    def mostrar_menu_conductor(self, user_id: str):
        """Muestra el menú principal y actualiza el estado"""
        self.message_service.mostrar_menu_conductor(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_menu", self.db)
    
    def handle_salir(self, user_id: str):
        """Maneja la salida del usuario"""
        self.message_service.despedir_usuario(user_id)
        sesion.actualizar_estado_chat(user_id, "inicial", self.db)
    
    # ===== FLUJOS DE GESTOR =====
    
    def handle_gestor_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú de gestor"""
        if text == "1":
            self.handle_ver_info_parqueadero_gestor(user_id)
        elif text == "2":
            self.handle_solicitar_actualizacion_cupos(user_id)
        elif text == "3":
            self.handle_salir(user_id)
        else:
            self.message_service.error_opcion_invalida_menu_principal(user_id)
            self.mostrar_menu_gestor(user_id)
    
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
    
    def handle_solicitar_actualizacion_cupos(self, user_id: str):
        """Solicita información para actualizar cupos"""
        self.message_service.solicitar_cupos_actualizacion(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_cambio_cupos", self.db)
    
    def handle_cupos_gestor(self, text: str, user_id: str):
        """Procesa la actualización de cupos del gestor"""
        try:
            # Parsear input: "cupos_libres,tiene_cupos"
            parts = text.split(',')
            if len(parts) != 2:
                raise ValueError("Formato incorrecto")
                
            cupos_libres = parts[0].strip()
            tiene_cupos = parts[1].strip().lower() == 'true'
            
            # Obtener parqueadero del gestor
            parqueadero_id = self.gestor_repo.obtener_parqueadero_id(user_id)
            if not parqueadero_id:
                self.message_service.error_parqueadero_no_encontrado(user_id)
                self.mostrar_menu_gestor(user_id)
                return
            
            # Actualizar cupos y enviar notificaciones
            result = self.parqueadero_repo.actualizar_cupos_con_notificacion(
                parqueadero_id, 
                cupos_libres, 
                tiene_cupos, 
                self.notification_service
            )
            
            self.message_service.confirmar_actualizacion_cupos(
                user_id, 
                cupos_libres, 
                result["notificaciones_enviadas"]
            )
            
        except (ValueError, IndexError):
            self.message_service.error_formato_cupos(user_id)
        
        self.mostrar_menu_gestor(user_id)
    
    def mostrar_menu_gestor(self, user_id: str):
        """Muestra el menú principal del gestor y actualiza el estado"""
        self.message_service.mostrar_menu_gestor(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_menu", self.db)