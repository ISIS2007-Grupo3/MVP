"""
Servicio especializado para mensajes de bienvenida y registro de usuarios
"""
from app.logic.send_message import send_message


class MensajeBienvenidaService:
    """
    Servicio enfocado en mensajes de bienvenida y proceso de registro.
    Responsabilidad: Comunicación inicial con usuarios nuevos y existentes.
    """
    
    def enviar_bienvenida(self, user_id: str):
        """Envía mensaje de bienvenida a nuevos usuarios"""
        send_message(user_id, "¡Hola! Bienvenido a la plataforma de cupos de parqueaderos!")
    
    def solicitar_nombre(self, user_id: str):
        """Solicita el nombre para completar el registro"""
        send_message(user_id, "Parece que no estás registrado. Por favor, envía tu nombre para registrarte.")
    
    def confirmar_registro(self, user_id: str, nombre: str):
        """Confirma el registro exitoso"""
        send_message(user_id, f"Gracias {nombre}, ahora estás registrado. Escribe cualquier mensaje para continuar.")
    
    def saludar_usuario_registrado(self, user_id: str, nombre: str):
        """Saluda a un usuario ya registrado"""
        send_message(user_id, f"Hola de nuevo {nombre} 👋🚘!")
