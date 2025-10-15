"""
Servicio especializado para mensajes generales del sistema
"""
from app.logic.send_message import send_message


class MensajeGeneralService:
    """
    Servicio para mensajes generales del sistema.
    Responsabilidad: Mensajes de despedida, ayuda y otros mensajes generales.
    """
    
    def despedir_usuario(self, user_id: str):
        """Despide al usuario al salir"""
        send_message(user_id, "👋 ¡Gracias por usar el servicio! Escribe cualquier mensaje para volver.")
