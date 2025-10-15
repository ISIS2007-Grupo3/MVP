"""
Servicio para manejar mensajes interactivos de WhatsApp Cloud API
Incluye botones, listas y respuestas rápidas
"""
import requests
import json
import os
from typing import List, Dict, Any, Optional
from enum import Enum

class InteractiveType(Enum):
    BUTTON = "button"
    LIST = "list"
    QUICK_REPLY = "quick_reply"

class WhatsAppInteractiveService:
    def __init__(self):
        self.api_url = "https://graph.facebook.com/v17.0"
        self.access_token = os.getenv("WHATSAPP_TOKEN")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID")
    
    def send_interactive_message(self, to: str, interactive_data: Dict[str, Any]) -> bool:
        """Envía mensaje interactivo a través de WhatsApp Cloud API"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual", 
                "to": to,
                "type": "interactive",
                "interactive": interactive_data
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Error enviando mensaje interactivo: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Excepción enviando mensaje interactivo: {e}")
            return False
    
    def create_button_message(self, header_text: str, body_text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Crea un mensaje con botones (máximo 3 botones)
        
        Args:
            header_text: Texto del header
            body_text: Texto del cuerpo del mensaje
            buttons: Lista de botones [{"id": "btn_1", "title": "Opción 1"}, ...]
        """
        if len(buttons) > 3:
            raise ValueError("Máximo 3 botones permitidos")
        
        button_components = []
        for button in buttons:
            button_components.append({
                "type": "reply",
                "reply": {
                    "id": button["id"],
                    "title": button["title"]
                }
            })
        
        return {
            "type": "button",
            "header": {
                "type": "text",
                "text": header_text
            },
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": button_components
            }
        }
    
    def create_list_message(self, header_text: str, body_text: str, 
                           button_text: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea un mensaje con lista desplegable
        
        Args:
            header_text: Texto del header
            body_text: Texto del cuerpo
            button_text: Texto del botón para abrir la lista
            sections: Lista de secciones con opciones
        """
        return {
            "type": "list",
            "header": {
                "type": "text",
                "text": header_text
            },
            "body": {
                "text": body_text
            },
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    
    def create_quick_reply_message(self, body_text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Crea mensaje con botones de respuesta rápida (máximo 3)
        
        Args:
            body_text: Texto del mensaje
            buttons: Lista de botones de respuesta rápida
        """
        if len(buttons) > 3:
            raise ValueError("Máximo 3 botones de respuesta rápida permitidos")
        
        button_components = []
        for button in buttons:
            button_components.append({
                "type": "reply",
                "reply": {
                    "id": button["id"],
                    "title": button["title"]
                }
            })
        
        return {
            "type": "button",
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": button_components
            }
        }

    # ===== MENSAJES ESPECÍFICOS DEL NEGOCIO =====
    
    def send_conductor_menu(self, user_id: str) -> bool:
        """Envía menú principal para conductores"""
        sections = [{
            "title": "Menú Principal",
            "rows": [
                {
                    "id": "ver_parqueaderos",
                    "title": "🅿️ Ver Parqueaderos",
                    "description": "Consulta parqueaderos con cupos disponibles"
                },
                {
                    "id": "salir",
                    "title": "👋 Salir",
                    "description": "Cerrar sesión del sistema"
                }
            ]
        }]
        
        interactive_data = self.create_list_message(
            header_text="🚗 Menú Conductor",
            body_text="Bienvenido al sistema de parqueaderos. Selecciona una opción para continuar:",
            button_text="📋 Ver opciones",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_gestor_menu(self, user_id: str) -> bool:
        """Envía menú principal para gestores"""
        sections = [{
            "title": "Menú Gestor",
            "rows": [
                {
                    "id": "ver_info_parqueadero",
                    "title": "ℹ️ Ver Información",
                    "description": "Consulta el estado de tu parqueadero"
                },
                {
                    "id": "actualizar_cupos",
                    "title": "📝 Actualizar Cupos",
                    "description": "Modifica la disponibilidad de espacios"
                },
                {
                    "id": "salir",
                    "title": "👋 Salir",
                    "description": "Cerrar sesión del sistema"
                }
            ]
        }]
        
        interactive_data = self.create_list_message(
            header_text="🏢 Menú Gestor",
            body_text="Panel de administración de parqueadero. Selecciona una opción:",
            button_text="⚙️ Ver opciones",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    # def send_subscription_menu(self, user_id: str) -> bool:
    #     """Envía menú de opciones de suscripción"""
    #     sections = [{
    #         "title": "Opciones de Suscripción",
    #         "rows": [
    #             {
    #                 "id": "suscribir_todos",
    #                 "title": "🌐 Todos",
    #                 "description": "Recibe notificaciones de todos los parqueaderos."
    #             },
    #             {
    #                 "id": "suscribir_especifico",
    #                 "title": "🅿️ Específico",
    #                 "description": "Elige un parqueadero particular para recibir notificaciones."
    #             },
    #             {
    #                 "id": "ver_suscripciones",
    #                 "title": "📋 Mis suscripciones",
    #                 "description": "Revisa tus suscripciones actuales."
    #             },
    #             {
    #                 "id": "desuscribir_todos",
    #                 "title": "❌ Desuscribirme",
    #                 "description": "Cancelar una o todas mis suscripciones."
    #             },
    #             {
    #                 "id": "volver_menu",
    #                 "title": "⬅️ Volver",
    #                 "description": "Regresar al menú principal."
    #             }
    #         ]
    #     }]
        
    #     interactive_data = self.create_list_message(
    #         header_text="🔔 Notificaciones",
    #         body_text="Gestiona tus suscripciones de notificaciones:",
    #         button_text="📝 Ver opciones",
    #         sections=sections
    #     )
    #     return self.send_interactive_message(user_id, interactive_data)
    
    # def send_subscriptions_list_with_unsubscribe(self, user_id: str, suscripciones: List[Any]) -> bool:
    #     """Envía lista interactiva de suscripciones con opciones de desuscripción"""
    #     print(f"🔍 send_subscriptions_list_with_unsubscribe llamado con {len(suscripciones) if suscripciones else 0} suscripciones")
    #     if not suscripciones:
    #         print("❌ No hay suscripciones, retornando False")
    #         return False
        
    #     rows = []
        
    #     # Primera opción: Desuscribirse de todo
    #     rows.append({
    #         "id": "desuscribir_todo",
    #         "title": "❌ Desuscribir todo",
    #         "description": "Cancelar todas mis suscripciones"
    #     })
        
    #     # Agregar cada suscripción individual
    #     for i, suscripcion in enumerate(suscripciones):
    #         if suscripcion["tipo"] == "global":
    #             rows.append({
    #                 "id": f"desuscribir_{i}",
    #                 "title": "🌐 Todos",
    #                 "description": f"Desde {self._formato_fecha_corto(suscripcion['fecha'])}"
    #             })
    #         else:
    #             # Truncar nombre del parqueadero si es muy largo
    #             nombre = suscripcion['parqueadero']
    #             nombre_truncado = nombre[:17] + "..." if len(nombre) > 17 else nombre
    #             rows.append({
    #                 "id": f"desuscribir_{i}",
    #                 "title": f"🅿️ {nombre_truncado}",
    #                 "description": f"Desde {self._formato_fecha_corto(suscripcion['fecha'])}"
    #             })
        
    #     # Agregar opción para volver
    #     rows.append({
    #         "id": "volver_suscripciones",
    #         "title": "⬅️ Volver",
    #         "description": "Regresar al menú de notificaciones"
    #     })
        
    #     sections = [{
    #         "title": "Mis Suscripciones",
    #         "rows": rows
    #     }]
        
    #     print(f"📋 Creando mensaje interactivo con {len(rows)} opciones")
    #     interactive_data = self.create_list_message(
    #         header_text="📋 Tus Suscripciones",
    #         body_text="Selecciona una opción para desuscribirte:",
    #         button_text="📝 Ver opciones",
    #         sections=sections
    #     )
    #     result = self.send_interactive_message(user_id, interactive_data)
    #     print(f"✅ Resultado del envío: {result}")
    #     return result
    
    def _formato_fecha_corto(self, fecha_str: str) -> str:
        """Convierte fecha a formato corto para descripciones"""
        try:
            from datetime import datetime
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            return fecha.strftime("%d/%m/%Y")
        except:
            return fecha_str[:10] if len(fecha_str) >= 10 else fecha_str
    
    def send_cupos_options(self, user_id: str) -> bool:
        """Envía opciones para actualizar cupos"""
        sections = [{
            "title": "Estado del Parqueadero",
            "rows": [
                {
                    "id": "cupos_lleno",
                    "title": "🔴 Lleno",
                    "description": "0 cupos disponibles"
                },
                {
                    "id": "cupos_pocos",
                    "title": "🟡 Pocos cupos",
                    "description": "1-5 cupos disponibles"
                },
                {
                    "id": "cupos_algunos",
                    "title": "🟢 Algunos cupos",
                    "description": "6-15 cupos disponibles"
                },
                {
                    "id": "cupos_muchos",
                    "title": "🟢 Muchos cupos",
                    "description": "16-30 cupos disponibles"
                },
                {
                    "id": "cupos_casi_vacio",
                    "title": "🔵 Casi vacío",
                    "description": "30+ cupos disponibles"
                },
                {
                    "id": "volver_menu_gestor",
                    "title": "⬅️ Volver al menú",
                    "description": "Cancelar y regresar"
                }
            ]
        }]
        
        interactive_data = self.create_list_message(
            header_text="📝 Actualizar Cupos",
            body_text="Selecciona el estado actual del parqueadero:",
            button_text="📊 Seleccionar estado",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_confirmation_cupos(self, user_id: str, descripcion: str, rango: str) -> bool:
        """Envía confirmación para actualización de cupos"""
        sections = [{
            "title": "Confirmación",
            "rows": [
                {
                    "id": "confirmar_cupos",
                    "title": "✅ Confirmar",
                    "description": "Guardar y notificar a conductores"
                },
                {
                    "id": "reseleccionar_cupos",
                    "title": "🔄 Cambiar",
                    "description": "Volver a elegir el estado"
                },
                {
                    "id": "cancelar_cupos",
                    "title": "❌ Cancelar",
                    "description": "Volver al menú principal"
                }
            ]
        }]
        
        interactive_data = self.create_list_message(
            header_text="⚠️ Confirmar Actualización",
            body_text=f"""Verifica que la información sea correcta:

📋 *Estado:* {descripcion}
🅿️ *Disponibilidad:* {rango}

Selecciona una acción:""",
            button_text="Opciones ",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_parqueaderos_con_detalles(self, user_id: str, parqueaderos: List[Any], pagina: int = 1) -> bool:
        """
        Envía lista de parqueaderos con cupos disponibles y opción de ver detalles con paginación
        Args:
            user_id: ID del usuario
            parqueaderos: Lista completa de parqueaderos
            pagina: Número de página actual (empieza en 1)
        """
        if not parqueaderos:
            return False
        
        from app.utils.tiempo_utils import tiempo_relativo
        
        # Configuración de paginación
        # Con paginación: 7 parqueaderos + 2 botones navegación + 1 volver = 10 items
        # Sin paginación: 9 parqueaderos + 1 volver = 10 items
        items_por_pagina = 7
        total_parqueaderos = len(parqueaderos)
        total_paginas = (total_parqueaderos + items_por_pagina - 1) // items_por_pagina
        
        # Validar página
        if pagina < 1:
            pagina = 1
        elif pagina > total_paginas:
            pagina = total_paginas
        
        # Calcular índices para la página actual
        inicio = (pagina - 1) * items_por_pagina
        fin = min(inicio + items_por_pagina, total_parqueaderos)
        
        rows = []
        
        # Agregar parqueaderos de la página actual
        for i in range(inicio, fin):
            parqueadero = parqueaderos[i]
            
            # Obtener última actualización
            ultima_actualizacion = "Sin actualizar"
            if hasattr(parqueadero, 'ultima_actualizacion') and parqueadero.ultima_actualizacion:
                ultima_actualizacion = tiempo_relativo(parqueadero.ultima_actualizacion)
            
            estado = parqueadero.estado_ocupacion if hasattr(parqueadero, 'estado_ocupacion') and parqueadero.estado_ocupacion else "Disponible"
            
            # Limitar el título a 22 caracteres (incluyendo emoji) para no exceder el límite de WhatsApp
            name_truncated = parqueadero.name[:19] + "..." if len(parqueadero.name) > 19 else parqueadero.name
            
            rows.append({
                "id": f"detalle_parqueadero_{i}",
                "title": f"🅿️ {name_truncated}",
                "description": f"{estado} • {ultima_actualizacion}"
            })
        
        # Agregar botones de navegación si hay múltiples páginas
        if total_paginas > 1:
            if pagina > 1:
                rows.append({
                    "id": f"pagina_anterior_{pagina - 1}",
                    "title": "⬅️ Página anterior",
                    "description": f"Ver página {pagina - 1} de {total_paginas}"
                })
            
            if pagina < total_paginas:
                rows.append({
                    "id": f"pagina_siguiente_{pagina + 1}",
                    "title": "➡️ Página siguiente",
                    "description": f"Ver página {pagina + 1} de {total_paginas}"
                })
        
        # Agregar opción para volver
        rows.append({
            "id": "volver_menu_conductor",
            "title": "⬅️ Volver al menú",
            "description": "Regresar al menú principal"
        })
        
        sections = [{
            "title": f"Parqueaderos (Pág. {pagina}/{total_paginas})" if total_paginas > 1 else "Parqueaderos con Cupos",
            "rows": rows
        }]
        
        body_text = f"Mostrando {fin - inicio} de {total_parqueaderos} parqueaderos. Selecciona uno para ver más detalles:" if total_paginas > 1 else "Selecciona un parqueadero para ver más detalles:"
        
        interactive_data = self.create_list_message(
            header_text="🅿️ Parqueaderos Disponibles",
            body_text=body_text,
            button_text="📋 Ver opciones",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_parqueaderos_list(self, user_id: str, parqueaderos: List[Any]) -> bool:
        """Envía lista de parqueaderos para suscripción"""
        if not parqueaderos:
            return False
        
        rows = []
        for i, parqueadero in enumerate(parqueaderos[:9]):  # Máximo 9 para dejar espacio al botón volver
            # Limitar el título a 22 caracteres (incluyendo emoji) para no exceder el límite de WhatsApp
            name_truncated = parqueadero.name[:19] + "..." if len(parqueadero.name) > 19 else parqueadero.name
            
            rows.append({
                "id": f"parqueadero_{i}",
                "title": f"🅿️ {name_truncated}",
                "description": f"📍 {parqueadero.ubicacion}"
            })
        
        # Agregar opción para volver
        rows.append({
            "id": "volver_suscripciones",
            "title": "⬅️ Volver",
            "description": "Regresar al menú de suscripciones"
        })
        
        sections = [{
            "title": "Parqueaderos Disponibles",
            "rows": rows
        }]
        
        interactive_data = self.create_list_message(
            header_text="🅿️ Suscripción Específica",
            body_text="Selecciona el parqueadero al que te quieres suscribir:",
            button_text="📝 Seleccionar",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)