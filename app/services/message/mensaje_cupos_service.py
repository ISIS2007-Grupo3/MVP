"""
Servicio especializado para mensajes de cupos (gestor)
"""
from app.logic.send_message import send_message
from app.services.whatsapp_interactive_service import WhatsAppInteractiveService


class MensajeCuposService:
    """
    Servicio enfocado en mensajes relacionados con actualización de cupos.
    Responsabilidad: Comunicar opciones y confirmaciones de actualización de cupos.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.interactive_service = WhatsAppInteractiveService()
    
    def solicitar_confirmacion_cupos(self, user_id: str, opcion: int, descripcion: str, rango: str):
        """Solicita confirmación antes de actualizar los cupos usando mensajes interactivos"""
        success = self.interactive_service.send_confirmation_cupos(user_id, descripcion, rango)
        if not success:
            # Fallback al mensaje de texto tradicional con formato descriptivo
            mensaje = f"""⚠️ *Confirmar Actualización*

Verifica que la información sea correcta:

📋 *Estado:* {descripcion}
🅿️ *Disponibilidad:* {rango}

Escribe el número de tu opción para confirmar:

✅ *1* - Confirmar actualización
   • Guardar cambios y notificar a conductores suscritos

🔄 *2* - Cambiar selección
   • Volver atrás para elegir otro estado

❌ *3* - Cancelar operación
   • Descartar cambios y volver al menú principal

💡 *Tip: Los conductores recibirán notificación si hay cupos disponibles*"""
            send_message(user_id, mensaje)
    
    def confirmar_actualizacion_cupos(self, user_id: str, cupos_libres: str, notificaciones_enviadas: int):
        """Confirma la actualización de cupos"""
        mensaje = f"""✅ *Cupos actualizados exitosamente*

🅿️ Cupos libres: {cupos_libres}
📢 Notificaciones enviadas: {notificaciones_enviadas}"""
        send_message(user_id, mensaje)
    
    def confirmar_actualizacion_cupos_con_descripcion(self, user_id: str, descripcion: str, cupos_libres: str, notificaciones_enviadas: int):
        """Confirma la actualización de cupos con descripción del estado"""
        mensaje = f"""✅ *Cupos actualizados exitosamente*

📋 *Estado:* {descripcion}
🅿️ *Cupos aproximados:* {cupos_libres}
📢 *Notificaciones enviadas:* {notificaciones_enviadas}

{self._obtener_emoji_notificaciones(notificaciones_enviadas)}
"""
        send_message(user_id, mensaje)
    
    def _obtener_emoji_notificaciones(self, cantidad: int) -> str:
        """Obtiene emoji apropiado según cantidad de notificaciones enviadas"""
        if cantidad == 0:
            return "ℹ️ No hay conductores suscritos actualmente"
        elif cantidad == 1:
            return "👤 Se notificó a 1 conductor"
        elif cantidad <= 5:
            return f"👥 Se notificó a {cantidad} conductores"
        else:
            return f"🚨 Se notificó a {cantidad} conductores - ¡Alto interés!"
    