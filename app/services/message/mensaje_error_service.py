"""
Servicio especializado para mensajes de error y validación
"""
from app.logic.send_message import send_message


class MensajeErrorService:
    """
    Servicio enfocado en mostrar mensajes de error y validación.
    Responsabilidad: Comunicar errores y guiar al usuario hacia opciones válidas.
    """
    
    def error_opcion_invalida_menu_principal(self, user_id: str):
        """Error cuando selecciona opción inválida en menú principal"""
        send_message(user_id, "❌ Opción no reconocida. Por favor, selecciona una opción del menú:")
    
    # def error_opcion_invalida_suscripciones(self, user_id: str):
    #     """Error cuando selecciona opción inválida en menú de suscripciones"""
    #     send_message(user_id, "❌ Opción no válida. Por favor, selecciona del menú de suscripciones:")
    
    def error_numero_invalido(self, user_id: str):
        """Error cuando envía un número inválido"""
        send_message(user_id, "❌ Número no válido. Por favor, selecciona una opción del menú:")
    
    def error_parqueadero_no_encontrado(self, user_id: str):
        """Error cuando no se encuentra el parqueadero"""
        send_message(user_id, "❌ Parqueadero no encontrado. Intenta de nuevo:")
    
    # def error_sin_suscripciones(self, user_id: str):
    #     """Error cuando no tiene suscripciones activas"""
    #     send_message(user_id, "ℹ️ No tienes suscripciones activas en este momento.")
    
    def error_general(self, user_id: str, mensaje_error: str):
        """Error general en suscripciones"""
        send_message(user_id, f"❌ Error: {mensaje_error}")
    
    def error_rol_no_reconocido(self, user_id: str):
        """Error cuando el rol del usuario no es reconocido"""
        send_message(user_id, "❌ Rol no reconocido. Por favor contacta al soporte técnico.")
    
    def error_formato_cupos(self, user_id: str):
        """Error en formato de actualización de cupos"""
        send_message(user_id, "❌ Opción no válida. Por favor, selecciona del menú de actualización:")
    
    # def error_comando_desuscripcion(self, user_id: str):
    #     """Error en comando de desuscripción"""
    #     send_message(user_id, "❌ Comando inválido. Usa 'desuscribir', 'desuscribir todo' o 'desuscribir [número]'")
    
    def error_confirmacion_cupos(self, user_id: str):
        """Error en la confirmación de cupos"""
        send_message(user_id, "❌ Opción no válida. Por favor, selecciona una opción del menú de confirmación:")
    
    def error_opcion_invalida(self, user_id: str):
        """Error genérico de opción inválida"""
        send_message(user_id, "❌ Opción no válida. Por favor, selecciona una opción del menú:")
