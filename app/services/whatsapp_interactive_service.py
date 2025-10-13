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
        interactive_data = self.create_button_message(
            header_text="🚗 Menú Conductor",
            body_text="Selecciona una opción:",
            buttons=[
                {"id": "ver_parqueaderos", "title": "🅿️ Ver Parqueaderos"},
                {"id": "suscripciones", "title": "🔔 Notificaciones"},
                {"id": "salir", "title": "👋 Salir"}
            ]
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_gestor_menu(self, user_id: str) -> bool:
        """Envía menú principal para gestores"""
        interactive_data = self.create_button_message(
            header_text="🏢 Menú Gestor",
            body_text="Selecciona una opción:",
            buttons=[
                {"id": "ver_info_parqueadero", "title": "ℹ️ Ver Info"},
                {"id": "actualizar_cupos", "title": "📝 Actualizar Cupos"},
                {"id": "salir", "title": "👋 Salir"}
            ]
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_suscripciones_menu(self, user_id: str) -> bool:
        """Envía menú de opciones de suscripción"""
        sections = [{
            "title": "Opciones de Suscripción",
            "rows": [
                {
                    "id": "suscribir_todos",
                    "title": "🌐 Todos los parqueaderos",
                    "description": "Recibe notificaciones de todos"
                },
                {
                    "id": "suscribir_especifico",
                    "title": "🅿️ Parqueadero específico",
                    "description": "Elige un parqueadero particular"
                },
                {
                    "id": "ver_suscripciones",
                    "title": "📋 Ver mis suscripciones",
                    "description": "Revisa tus suscripciones actuales"
                },
                {
                    "id": "desuscribir_todos",
                    "title": "❌ Desuscribir todo",
                    "description": "Cancelar todas las notificaciones"
                },
                {
                    "id": "volver_menu",
                    "title": "⬅️ Volver al menú",
                    "description": "Regresar al menú principal"
                }
            ]
        }]
        
        interactive_data = self.create_list_message(
            header_text="🔔 Notificaciones",
            body_text="Gestiona tus suscripciones de notificaciones:",
            button_text="📝 Ver opciones",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_cupos_options(self, user_id: str) -> bool:
        """Envía opciones para actualizar cupos"""
        sections = [{
            "title": "Estado del Parqueadero",
            "rows": [
                {
                    "id": "cupos_lleno",
                    "title": "🔴 Parqueadero lleno",
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
        interactive_data = self.create_quick_reply_message(
            body_text=f"""⚠️ *Confirmar Actualización*

📋 *Estado:* {descripcion}
🅿️ *Rango:* {rango}

¿Es correcto este estado del parqueadero?""",
            buttons=[
                {"id": "confirmar_cupos", "title": "✅ Confirmar"},
                {"id": "reseleccionar_cupos", "title": "🔄 Cambiar"},
                {"id": "cancelar_cupos", "title": "❌ Cancelar"}
            ]
        )
        return self.send_interactive_message(user_id, interactive_data)
    
    def send_parqueaderos_list(self, user_id: str, parqueaderos: List[Any]) -> bool:
        """Envía lista de parqueaderos para suscripción"""
        if not parqueaderos:
            return False
        
        rows = []
        for i, parqueadero in enumerate(parqueaderos):
            rows.append({
                "id": f"parqueadero_{i}",
                "title": f"🅿️ {parqueadero.name}",
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
            "rows": rows[:10]  # WhatsApp permite máximo 10 filas
        }]
        
        interactive_data = self.create_list_message(
            header_text="🅿️ Suscripción Específica",
            body_text="Selecciona el parqueadero al que te quieres suscribir:",
            button_text="📝 Seleccionar",
            sections=sections
        )
        return self.send_interactive_message(user_id, interactive_data)