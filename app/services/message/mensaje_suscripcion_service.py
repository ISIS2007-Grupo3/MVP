"""
Servicio especializado para mensajes de suscripciones y notificaciones
"""
from app.logic.send_message import send_message
from app.utils.tiempo_utils import formatear_tiempo_para_usuario
from app.services.whatsapp_interactive_service import WhatsAppInteractiveService
from typing import List


class MensajeSuscripcionService:
    """
    Servicio enfocado en mensajes relacionados con suscripciones.
    Responsabilidad: Comunicar estado y cambios en suscripciones.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.interactive_service = WhatsAppInteractiveService()
    
    def confirmar_suscripcion_global(self, user_id: str):
        """Confirma suscripción a todos los parqueaderos"""
        send_message(user_id, "✅ Te has suscrito a notificaciones de *todos* los parqueaderos!")
    
    def confirmar_suscripcion_especifica(self, user_id: str, nombre_parqueadero: str):
        """Confirma suscripción a un parqueadero específico"""
        send_message(user_id, f"🔔 Te has suscrito a notificaciones del parqueadero: *{nombre_parqueadero}*")
    
    def confirmar_desuscripcion_total(self, user_id: str):
        """Confirma desuscripción de todas las notificaciones"""
        send_message(user_id, "✅ Te has desuscrito de todas las notificaciones correctamente.")
    
    def confirmar_desuscripcion_especifica(self, user_id: str, nombre_parqueadero: str):
        """Confirma desuscripción de un parqueadero específico"""
        send_message(user_id, f"❌ Te has desuscrito del parqueadero: *{nombre_parqueadero}*")
    
    def confirmar_desuscripcion_parqueadero(self, user_id: str, nombre_parqueadero: str):
        """Confirma desuscripción de un parqueadero específico (alias)"""
        send_message(user_id, f"✅ Te has desuscrito de '{nombre_parqueadero}' correctamente")
    
    def mostrar_suscripciones_actuales(self, user_id: str, suscripciones: List) -> bool:
        """Muestra las suscripciones actuales del conductor con menú interactivo"""
        print(f"🔍 mostrar_suscripciones_actuales: {len(suscripciones) if suscripciones else 0} suscripciones")
        if suscripciones:
            # Intentar mostrar menú interactivo
            success = self.interactive_service.send_subscriptions_list_with_unsubscribe(user_id, suscripciones)
            print(f"📊 Resultado del servicio interactivo: {success}")
            if success:
                return True
            
            # Fallback a mensaje de texto
            mensaje = "*Tus suscripciones actuales:*\n\n"
            for i, suscripcion in enumerate(suscripciones, 1):
                if suscripcion["tipo"] == "global":
                    mensaje += f"{i}️⃣ 🌐 Todos los parqueaderos\n"
                else:
                    mensaje += f"{i}️⃣ 🅿️ {suscripcion['parqueadero']}\n"
                mensaje += f"   📅 Desde: {formatear_tiempo_para_usuario(suscripcion['fecha'])}\n\n"
            
            mensaje += "Para desuscribirte, usa el menú de notificaciones ➡️ Opción ❌ Desuscribirme"
        else:
            mensaje = "❌ No tienes suscripciones activas"
        
        send_message(user_id, mensaje)
        return False
    
    def mostrar_ayuda_desuscripcion(self, user_id: str, suscripciones: List):
        """Muestra ayuda para comandos de desuscripción"""
        mensaje = "*Tus suscripciones actuales:*\n\n"
        for i, suscripcion in enumerate(suscripciones, 1):
            if suscripcion["tipo"] == "global":
                mensaje += f"{i}️⃣ 🌐 Todos los parqueaderos\n"
            else:
                mensaje += f"{i}️⃣ 🅿️ {suscripcion['parqueadero']}\n"
        
        mensaje += "\nEscribe 'desuscribir todo' o 'desuscribir [número]' para desuscribirte"
        send_message(user_id, mensaje)
    
    def informar_desuscripcion_especifica_limitada(self, user_id: str):
        """Informa sobre limitación de desuscripción específica"""
        send_message(user_id, "Para desuscribirte de parqueaderos específicos, usa el menú de suscripciones")
    
    def crear_notificacion_cupo_liberado(self, parqueadero) -> str:
        """Crea el mensaje de notificación cuando se libera un cupo"""
        # Usar rango si está disponible, sino usar cupos_libres tradicional
        info_cupos = parqueadero.rango_cupos or f"~{parqueadero.cupos_libres} cupos"
        estado = parqueadero.estado_ocupacion or "Cupos disponibles"
        
        return f"""🚗 ¡CUPO DISPONIBLE! 🅿️

📍 *{parqueadero.name}*
📌 Ubicación: {parqueadero.ubicacion}
📊 Estado: {estado}
🅿️ Disponibilidad: {info_cupos}

¡Apúrate antes de que se agote!

Para desuscribirte, navega al menú de notificaciones y selecciona "Desuscribirme". """
    
    def enviar_notificacion_cupo(self, user_id: str, mensaje: str):
        """Envía una notificación de cupo liberado"""
        send_message(user_id, mensaje)
