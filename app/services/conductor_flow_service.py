"""
Servicio para manejar los flujos de conversación de conductores en WhatsApp
"""
from app.services.whatsapp_message_service import WhatsAppMessageService
from app.services.notification_service import NotificationService
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.logic.parqueaderos import obtener_parqueaderos_con_cupos
import app.logic.sesion as sesion


class ConductorFlowService:
    """
    Servicio especializado para flujos de conversación de conductores
    Maneja consultas de parqueaderos, suscripciones y notificaciones
    """
    
    def __init__(self, db):
        self.db = db
        self.message_service = WhatsAppMessageService(db)
        self.notification_service = NotificationService(db)
        self.parqueadero_repo = ParqueaderoRepository(db)
    
    # ===== MENÚ PRINCIPAL =====
    
    def mostrar_menu_conductor(self, user_id: str):
        """Muestra el menú principal y actualiza el estado"""
        self.message_service.mostrar_menu_conductor(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_menu", self.db)
    
    def handle_conductor_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú principal de conductor (texto e interactivo)"""
        # Manejar respuestas de botones interactivos
        if text == "ver_parqueaderos":
            self.handle_ver_parqueaderos(user_id)
        elif text == "suscripciones":
            self.handle_mostrar_menu_suscripciones(user_id)
        elif text == "salir":
            self.handle_salir(user_id)
        # Mantener compatibilidad con números tradicionales
        elif text == "1":
            self.handle_ver_parqueaderos(user_id)
        elif text == "2":
            self.handle_mostrar_menu_suscripciones(user_id)
        elif text == "3":
            self.handle_salir(user_id)
        else:
            self.message_service.error_opcion_invalida_menu_principal(user_id)
            self.mostrar_menu_conductor(user_id)
    
    # ===== CONSULTA DE PARQUEADEROS =====
    
    def handle_ver_parqueaderos(self, user_id: str, pagina: int = 1):
        """Muestra parqueaderos con cupos disponibles con detalles y paginación"""
        self.message_service.mostrar_consultando_parqueaderos(user_id)
        parqueaderos = obtener_parqueaderos_con_cupos(self.db)
        
        if parqueaderos:
            # Enviar lista interactiva con opción de ver detalles y paginación
            success = self.message_service.mostrar_parqueaderos_interactivos(user_id, parqueaderos, pagina)
            
            if success:
                # Guardar IDs de parqueaderos y página actual en contexto para referencia
                parqueaderos_ids = [p.id for p in parqueaderos]
                sesion.actualizar_contexto_temporal(user_id, {
                    "parqueaderos_consulta": parqueaderos_ids,
                    "pagina_actual": pagina
                }, self.db)
                sesion.actualizar_estado_chat(user_id, "viendo_parqueaderos", self.db)
            else:
                # Fallback: mostrar solo texto y volver al menú
                self.message_service.mostrar_parqueaderos_disponibles(user_id, parqueaderos)
                self.mostrar_menu_conductor(user_id)
        else:
            self.message_service.mostrar_parqueaderos_disponibles(user_id, parqueaderos)
            self.mostrar_menu_conductor(user_id)
    
    def handle_seleccion_parqueadero_detalles(self, text: str, user_id: str):
        """Maneja la selección de un parqueadero para ver detalles o navegación de páginas"""
        try:
            # Obtener contexto actual
            usuario = sesion.obtener_usuario(user_id, self.db)
            contexto_temporal = usuario.estado_chat.contexto_temporal or {}
            parqueaderos_ids = contexto_temporal.get('parqueaderos_consulta', [])
            pagina_actual = contexto_temporal.get('pagina_actual', 1)
            
            # Manejar opción de volver
            if text == "volver_menu_conductor":
                self.mostrar_menu_conductor(user_id)
                return
            
            # Manejar navegación de páginas (anterior)
            if text.startswith("pagina_anterior_"):
                nueva_pagina = int(text.split("_")[2])
                self.handle_ver_parqueaderos(user_id, nueva_pagina)
                return
            
            # Manejar navegación de páginas (siguiente)
            if text.startswith("pagina_siguiente_"):
                nueva_pagina = int(text.split("_")[2])
                self.handle_ver_parqueaderos(user_id, nueva_pagina)
                return
            
            # Manejar selección interactiva de parqueadero
            if text.startswith("detalle_parqueadero_"):
                index = int(text.split("_")[2])
                
                if 0 <= index < len(parqueaderos_ids):
                    parqueadero_id = parqueaderos_ids[index]
                    parqueadero = self.parqueadero_repo.find_by_id(parqueadero_id)
                    
                    if parqueadero:
                        self.message_service.mostrar_detalle_parqueadero(user_id, parqueadero)
                    else:
                        self.message_service.error_parqueadero_no_encontrado(user_id)
                else:
                    self.message_service.error_numero_invalido(user_id)
                
                # Volver a mostrar la lista en la página actual
                self.handle_ver_parqueaderos(user_id, pagina_actual)
                return
            
            # Manejar entrada tradicional por números
            opcion = int(text)
            
            if opcion == len(parqueaderos_ids) + 1:
                # Volver al menú
                self.mostrar_menu_conductor(user_id)
                return
            
            if 1 <= opcion <= len(parqueaderos_ids):
                parqueadero_id = parqueaderos_ids[opcion - 1]
                parqueadero = self.parqueadero_repo.find_by_id(parqueadero_id)
                
                if parqueadero:
                    self.message_service.mostrar_detalle_parqueadero(user_id, parqueadero)
                else:
                    self.message_service.error_parqueadero_no_encontrado(user_id)
                
                # Volver a mostrar la lista en la página actual
                self.handle_ver_parqueaderos(user_id, pagina_actual)
            else:
                self.message_service.error_numero_invalido(user_id)
                self.handle_ver_parqueaderos(user_id, pagina_actual)
                
        except ValueError:
            usuario = sesion.obtener_usuario(user_id, self.db)
            contexto_temporal = usuario.estado_chat.contexto_temporal or {}
            pagina_actual = contexto_temporal.get('pagina_actual', 1)
            self.message_service.error_numero_invalido(user_id)
            self.handle_ver_parqueaderos(user_id, pagina_actual)
        except Exception as e:
            print(f"Error en selección de parqueadero: {e}")
            import traceback
            traceback.print_exc()
            self.message_service.error_suscripcion_general(user_id, "Error al consultar parqueadero")
            self.mostrar_menu_conductor(user_id)
    
    # ===== GESTIÓN DE SUSCRIPCIONES =====
    
    def handle_mostrar_menu_suscripciones(self, user_id: str):
        """Muestra el menú de suscripciones"""
        self.message_service.mostrar_menu_suscripciones(user_id)
        sesion.actualizar_estado_chat(user_id, "esperando_opcion_suscripcion", self.db)
    
    def handle_suscripcion_menu_option(self, text: str, user_id: str):
        """Procesa las opciones del menú de suscripciones (texto e interactivo)"""
        # Manejar respuestas de lista interactiva
        if text == "suscribir_todos":
            self._suscribir_todos(user_id)
            
        elif text == "suscribir_especifico":
            self.mostrar_parqueaderos_para_suscripcion(user_id)
            
        elif text == "ver_suscripciones":
            self.mostrar_suscripciones_actuales(user_id)
            
        elif text == "desuscribir_todos":
            self._desuscribir_todos(user_id)
            
        elif text == "volver_menu":
            self.mostrar_menu_conductor(user_id)
            
        # Mantener compatibilidad con números tradicionales
        elif text == "1":
            self._suscribir_todos(user_id)
            
        elif text == "2":
            self.mostrar_parqueaderos_para_suscripcion(user_id)
            
        elif text == "3":
            self.mostrar_suscripciones_actuales(user_id)
            
        elif text == "4":
            self._desuscribir_todos(user_id)
            
        elif text == "5":
            self.mostrar_menu_conductor(user_id)
            
        else:
            self.message_service.error_opcion_invalida_suscripciones(user_id)
            self.handle_mostrar_menu_suscripciones(user_id)
    
    def _suscribir_todos(self, user_id: str):
        """Suscribe al conductor a todos los parqueaderos"""
        result = self.notification_service.suscribir_conductor(user_id, None)
        if not result["success"]:
            self.message_service.error_suscripcion_general(user_id, result["message"])
            self.handle_mostrar_menu_suscripciones(user_id)
            return
        # Suscripción exitosa, volver al menú principal
        self.mostrar_menu_conductor(user_id)
    
    def _desuscribir_todos(self, user_id: str):
        """Desuscribe al conductor de todos los parqueaderos"""
        result = self.notification_service.desuscribir_conductor(user_id, None)
        if not result["success"]:
            # Si no tenía suscripciones, volver al menú de suscripciones
            if result.get("had_subscriptions") == False:
                self.handle_mostrar_menu_suscripciones(user_id)
                return
            else:
                self.message_service.error_suscripcion_general(user_id, result["message"])
                self.mostrar_menu_conductor(user_id)
                return
        # Desuscripción exitosa, volver al menú principal
        self.mostrar_menu_conductor(user_id)
    
    # ===== SUSCRIPCIÓN A PARQUEADERO ESPECÍFICO =====
    
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
        """Maneja la selección de parqueadero para suscripción (texto e interactivo)"""
        try:
            # Manejar respuestas de lista interactiva
            if text == "volver_suscripciones":
                self.handle_mostrar_menu_suscripciones(user_id)
                return
                
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
                        self.message_service.error_suscripcion_general(user_id, result["message"])
                    else:
                        # Limpiar contexto temporal después de suscripción exitosa
                        sesion.actualizar_contexto_temporal(user_id, {}, self.db)
                else:
                    self.message_service.error_numero_invalido(user_id)
                    
                self.mostrar_menu_conductor(user_id)
                return
            
            # Manejar entrada de texto tradicional (números)
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
    
    # ===== VER SUSCRIPCIONES =====
    
    def mostrar_suscripciones_actuales(self, user_id: str):
        """Muestra las suscripciones actuales del conductor con menú interactivo"""
        suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
        
        if not suscripciones:
            self.message_service.mostrar_suscripciones_actuales(user_id, suscripciones)
            self.mostrar_menu_conductor(user_id)
            return
        
        # Mostrar menú interactivo y cambiar estado si fue exitoso
        success = self.message_service.mostrar_suscripciones_actuales(user_id, suscripciones)
        if success:
            # Guardar suscripciones en contexto para manejar desuscripción
            sesion.actualizar_contexto_temporal(user_id, {"suscripciones": suscripciones}, self.db)
            sesion.actualizar_estado_chat(user_id, "gestionando_suscripciones", self.db)
        else:
            # Fallback: volver al menú principal
            self.mostrar_menu_conductor(user_id)
    
    def handle_gestion_suscripciones(self, text: str, user_id: str):
        """Maneja la gestión interactiva de suscripciones (desuscripción)"""
        try:
            # Obtener contexto
            usuario = sesion.obtener_usuario(user_id, self.db)
            contexto_temporal = usuario.estado_chat.contexto_temporal or {}
            suscripciones = contexto_temporal.get('suscripciones', [])
            
            # Manejar opción de volver
            if text == "volver_suscripciones":
                self.handle_mostrar_menu_suscripciones(user_id)
                return
            
            # Manejar desuscribir todo
            if text == "desuscribir_todo":
                result = self.notification_service.desuscribir_conductor(user_id, None)
                if result["success"]:
                    self.message_service.confirmar_desuscripcion_total(user_id)
                else:
                    self.message_service.error_suscripcion_general(user_id, result["message"])
                self.mostrar_menu_conductor(user_id)
                return
            
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
                                self.message_service.confirmar_desuscripcion_total(user_id)
                            else:
                                self.message_service.error_suscripcion_general(user_id, result["message"])
                        else:
                            # Desuscribir de parqueadero específico
                            parqueadero_id = suscripcion.get("parqueadero_id")
                            if parqueadero_id:
                                result = self.notification_service.desuscribir_conductor(user_id, parqueadero_id)
                                if result["success"]:
                                    self.message_service.confirmar_desuscripcion_parqueadero(user_id, suscripcion['parqueadero'])
                                else:
                                    self.message_service.error_suscripcion_general(user_id, result["message"])
                            else:
                                self.message_service.error_suscripcion_general(user_id, "No se pudo identificar el parqueadero")
                        
                        self.mostrar_menu_conductor(user_id)
                        return
                    else:
                        self.message_service.error_numero_invalido(user_id)
                        self.mostrar_suscripciones_actuales(user_id)
                        return
                        
                except (ValueError, IndexError) as e:
                    print(f"Error procesando desuscripción: {e}")
                    self.message_service.error_numero_invalido(user_id)
                    self.mostrar_suscripciones_actuales(user_id)
                    return
            
            # Opción no reconocida
            self.message_service.error_opcion_invalida(user_id)
            self.mostrar_suscripciones_actuales(user_id)
            
        except Exception as e:
            print(f"Error en gestión de suscripciones: {e}")
            import traceback
            traceback.print_exc()
            self.message_service.error_suscripcion_general(user_id, "Error al procesar la solicitud")
            self.mostrar_menu_conductor(user_id)
    
    # ===== COMANDOS DE DESUSCRIPCIÓN =====
    
    def handle_desuscribir_comando(self, text: str, user_id: str):
        """Maneja comandos de desuscripción desde cualquier punto de la conversación"""
        comando_parts = text.lower().split()
        
        if len(comando_parts) == 1:  # Solo "desuscribir"
            suscripciones = self.notification_service.listar_suscripciones_conductor(user_id)
            
            if not suscripciones:
                self.message_service.error_sin_suscripciones(user_id)
                self.message_service.mostrar_menu_suscripciones(user_id)
                return
                
            self.message_service.mostrar_ayuda_desuscripcion(user_id, suscripciones)
            
        elif len(comando_parts) == 2:
            if comando_parts[1] == "todo":
                # Desuscribir de todo
                self.notification_service.desuscribir_conductor(user_id, None)
                self.mostrar_menu_conductor(user_id)
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
    
    # ===== SALIDA =====
    
    def handle_salir(self, user_id: str):
        """Maneja la salida del usuario"""
        self.message_service.despedir_usuario(user_id)
        sesion.actualizar_estado_chat(user_id, "inicial", self.db)
