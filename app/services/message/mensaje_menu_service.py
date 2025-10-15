"""
Servicio especializado para mensajes de menú de WhatsApp
"""
from app.logic.send_message import send_message
from app.services.whatsapp_interactive_service import WhatsAppInteractiveService


class MensajeMenuService:
    """
    Servicio enfocado en mostrar menús interactivos y de texto.
    Responsabilidad: Presentar opciones de navegación a los usuarios.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.interactive_service = WhatsAppInteractiveService()
    
    def mostrar_menu_conductor(self, user_id: str):
        """Muestra el menú principal para conductores usando mensajes interactivos"""
        success = self.interactive_service.send_conductor_menu(user_id)
        if not success:
            # Fallback al mensaje de texto tradicional
            menu = """🚗 *Menú Conductor*

Bienvenido al sistema de parqueaderos. Escribe el número de tu opción:

1️⃣ Ver Parqueaderos
   📍 Consulta parqueaderos con cupos disponibles

2️⃣ Salir
   👋 Cerrar sesión del sistema"""
            send_message(user_id, menu)
    
#     def mostrar_menu_suscripciones(self, user_id: str):
#         """Muestra el menú de opciones de suscripción usando mensajes interactivos"""
#         success = self.interactive_service.send_subscription_menu(user_id)
#         if not success:
#             # Fallback al mensaje de texto tradicional
#             menu = """🔔 *Notificaciones de Parqueaderos*

# Gestiona tus suscripciones de notificaciones. Escribe el número de tu opción:

# 1️⃣ Todos los parqueaderos
#    🌐 Recibe notificaciones de todos

# 2️⃣ Parqueadero específico
#    🅿️ Elige un parqueadero particular

# 3️⃣ Ver mis suscripciones
#    📋 Revisa tus suscripciones actuales

# 4️⃣ Desuscribir todo
#    ❌ Cancelar todas las notificaciones

# 5️⃣ Volver al menú
#    ⬅️ Regresar al menú principal"""
#             send_message(user_id, menu)
    
    def mostrar_menu_gestor(self, user_id: str):
        """Muestra el menú principal para gestores usando mensajes interactivos"""
        success = self.interactive_service.send_gestor_menu(user_id)
        if not success:
            # Fallback al mensaje de texto tradicional
            menu = """🏢 *Menú Gestor de Parqueadero*

Panel de administración. Escribe el número de tu opción:

1️⃣ Ver Información
   ℹ️ Consulta el estado de tu parqueadero

2️⃣ Actualizar Cupos
   📝 Modifica la disponibilidad de espacios

3️⃣ Salir
   👋 Cerrar sesión del sistema"""
            send_message(user_id, menu)
    
    def mostrar_menu_cupos(self, user_id: str):
        """Solicita información para actualizar cupos usando mensajes interactivos"""
        success = self.interactive_service.send_cupos_options(user_id)
        if not success:
            # Fallback al mensaje de texto tradicional
            mensaje = """📝 *Actualizar Estado del Parqueadero*

Selecciona el estado actual. Escribe el número de tu opción:

🔴 *1* - Parqueadero lleno
   • 0 cupos disponibles

🟡 *2* - Pocos cupos
   • 1-5 cupos disponibles

🟢 *3* - Algunos cupos
   • 6-15 cupos disponibles

🟢 *4* - Muchos cupos
   • 16-30 cupos disponibles

🔵 *5* - Casi vacío
   • 30+ cupos disponibles

⬅️ *6* - Volver al menú
   • Cancelar y regresar

💡 *Las opciones 2-5 notificarán a conductores suscritos*"""
            send_message(user_id, mensaje)
