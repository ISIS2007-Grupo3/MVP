"""
Servicio especializado para mensajes de parqueaderos
"""
from app.logic.send_message import send_message
from app.utils.tiempo_utils import formatear_tiempo_para_usuario
from app.services.whatsapp_interactive_service import WhatsAppInteractiveService
from typing import List


class MensajeParqueaderoService:
    """
    Servicio enfocado en mensajes relacionados con parqueaderos.
    Responsabilidad: Mostrar información de parqueaderos y sus detalles.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.interactive_service = WhatsAppInteractiveService()
    
    def mostrar_parqueaderos_interactivos(self, user_id: str, parqueaderos: List, pagina: int = 1) -> bool:
        """Muestra lista interactiva de parqueaderos con opción de ver detalles y paginación"""
        if not parqueaderos:
            return False
        return self.interactive_service.send_parqueaderos_con_detalles(user_id, parqueaderos, pagina)
    
    def mostrar_parqueaderos_disponibles(self, user_id: str, parqueaderos: List):
        """Muestra lista de parqueaderos con cupos disponibles (fallback texto)"""
        if parqueaderos:
            mensaje = "*Parqueaderos con cupos disponibles:*\n\n"
            for p in parqueaderos:
                # Mostrar rango si está disponible, sino usar cupos tradicionales
                info_cupos = p.rango_cupos or f"~{p.cupos_libres} cupos"
                estado = p.estado_ocupacion or "Cupos disponibles"
                
                mensaje += f"🅿️ *{p.name}*\n"
                mensaje += f"   📍 {p.ubicacion}\n"
                mensaje += f"   📊 {estado}\n"
                mensaje += f"   🚗 Disponibilidad: {info_cupos}\n"
                mensaje += f"   🕐 Actualizado: {formatear_tiempo_para_usuario(p.ultima_actualizacion)}\n\n"
            send_message(user_id, mensaje)
        else:
            send_message(user_id, "No hay parqueaderos con cupos disponibles en este momento.")
    
    def mostrar_detalle_parqueadero(self, user_id: str, parqueadero):
        """Muestra información detallada de un parqueadero específico"""
        info_cupos = parqueadero.rango_cupos or f"~{parqueadero.cupos_libres} cupos"
        estado = parqueadero.estado_ocupacion or "Cupos disponibles"
        
        mensaje = f"""🅿️ *{parqueadero.name}*

📍 *Ubicación:*
{parqueadero.ubicacion}

📊 *Estado Actual:*
{estado}

🚗 *Disponibilidad:*
{info_cupos}

🕐 *Última Actualización:*
{formatear_tiempo_para_usuario(parqueadero.ultima_actualizacion)}

💡 *Tip:* Puedes suscribirte a este parqueadero para recibir notificaciones cuando haya cupos disponibles."""
        
        send_message(user_id, mensaje)
    
    def mostrar_parqueaderos_para_suscripcion(self, user_id: str, parqueaderos: List):
        """Muestra parqueaderos disponibles para suscripción usando mensajes interactivos"""
        if parqueaderos:
            success = self.interactive_service.send_parqueaderos_list(user_id, parqueaderos)
            if not success:
                # Fallback al mensaje de texto tradicional
                mensaje = "*Parqueaderos disponibles:*\n\n"
                for i, p in enumerate(parqueaderos, 1):
                    mensaje += f"{i}️⃣ *{p.name}*\n   📍 {p.ubicacion}\n\n"
                mensaje += f"{len(parqueaderos) + 1}️⃣ Volver al menú de suscripciones\n\n"
                mensaje += "Escribe el número del parqueadero al que te quieres suscribir:"
                send_message(user_id, mensaje)
        else:
            send_message(user_id, "❌ No hay parqueaderos disponibles")
    
    def mostrar_informacion_parqueadero(self, user_id: str, parqueadero):
        """Muestra información detallada de un parqueadero (vista de gestor)"""
        # Mostrar rango si está disponible
        info_cupos = parqueadero.rango_cupos or f"~{parqueadero.cupos_libres}"
        estado = parqueadero.estado_ocupacion or ("Disponible" if parqueadero.tiene_cupos else "Lleno")
        
        mensaje = f"""🏢 *Información del Parqueadero*

📍 *Nombre:* {parqueadero.name}
📌 *Ubicación:* {parqueadero.ubicacion}
🚗 *Capacidad:* {parqueadero.capacidad}
📊 *Estado actual:* {estado}
🅿️ *Disponibilidad:* {info_cupos}
✅ *Tiene cupos:* {'Sí' if parqueadero.tiene_cupos else 'No'}
🕐 *Última actualización:* {formatear_tiempo_para_usuario(parqueadero.ultima_actualizacion)}"""
        send_message(user_id, mensaje)
    
    def mostrar_consultando_parqueaderos(self, user_id: str):
        """Mensaje mientras consulta parqueaderos"""
        send_message(user_id, "🅿️ Consultando parqueaderos disponibles...")
