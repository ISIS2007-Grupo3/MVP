from app.models.whatsapp_webhook import WebhookPayload
from app.logic.send_message import send_message
from app.models.whatsapp_webhook import Message
import app.logic.sesion as sesion
user_states = {}

def handle_registro_inicial(to, db):
    sesion.crear_usuario(to, db)
    send_message(to, "Parece que no estás registrado. Por favor, envía tu nombre para registrarte.")
    sesion.actualizar_estado_registro(to, "esperando_nombre", db)
    return

def handle_registro(msg: Message, db):
    usuario = sesion.obtener_usuario(msg.from_, db)
    if usuario.estado_registro == "esperando_nombre":
        sesion.actualizar_nombre(msg.from_, msg.text.body, db)
        usuario = sesion.obtener_usuario(msg.from_, db)
        send_message(msg.from_, f"Gracias {usuario.name}, ahora estás registrado. Puedes escribir 'menu' para ver las opciones.")
        sesion.actualizar_estado_registro(msg.from_, "completo", db)
        return usuario
    return None
    
def handle_login(msg: Message, db) -> sesion.User | None:
    sesion_usuario = sesion.obtener_usuario(msg.from_, db)
    if not sesion_usuario:
        send_message(msg.from_, "Hola! Bienvenido a la plataforma de cupos de parqueaderos!")
        handle_registro_inicial(msg.from_, db)
        return None
    if not sesion_usuario.estado_registro == "completo":
        usuario_registrado = handle_registro(msg, db)
        return usuario_registrado
    print("QUESOOOOOOOO")
    send_message(msg.from_, f"Hola de nuevo {sesion_usuario.name}! 👋 \n")
    return sesion_usuario

    

def handle_message(payload: WebhookPayload, db):
    msg = payload.get_mensaje()
    print(msg)
    if not msg or not msg.text:
        return None
    
    usuario = handle_login(msg, db)
    to = msg.from_
    text = msg.text.body.lower()
    print(text)
    if not usuario:
        return
    if not usuario.estado_registro == "completo":
        return
    sesion_usuario = sesion.obtener_usuario(to, db)
    if usuario.rol == "conductor":
        handle_conductor(text, to)
    return

def handle_conductor(text, to):
    menu= """
    🚗 Menú Conductor:
    1️⃣ Ver parqueaderos disponibles
    2️⃣ Salir
    """
    send_message(to, menu)
    # if text  == "menu":
    #     send_message(to, "🚗 Menú Conductor:\n 1️⃣ Ver parqueaderos disponibles\n 2️⃣ Salir")
    #     user_states[to] = "esperando opcion menu"
    #     return
    
    # if user_states[to] == "esperando opcion menu":
    #     if "1" == text:
    #         send_message(to, "No hay parqueaderos disponibles")
    #         send_message(to, "🚗 Menú Conductor:\n 1️⃣ Ver parqueaderos disponibles\n 2️⃣ Salir")
    #     elif "2" == text:
    #         send_message(to, "Gracias por usar el servicio!")
    #         user_states.pop(to)
    #     else:
    #         send_message(to, "Opción invalida")
    send_message(to, "Queso")
    return