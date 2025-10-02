from app.models.whatsapp_webhook import WebhookPayload
from app.logic.send_message import send_message

user_states = {}

def handle_message(payload: WebhookPayload, phone_number_id):
    msg = payload.get_mensaje()
    if not msg or not msg.text:
        return None
    
    to = msg.from_
    text = msg.text.body.lower()
    print(text)
    if to not in user_states:
        if text != "menu":
            send_message(to, "Bienvenido! \n Para ver el menú escribe 'menu'", phone_number_id)
            return
    handle_conductor(text, phone_number_id, to)
    return

def handle_conductor(text, phone_number_id, to):
    if text  == "menu":
        send_message(to, "🚗 Menú Conductor:\n 1️⃣ Ver parqueaderos disponibles\n 2️⃣ Salir", phone_number_id)
        user_states[to] = "esperando opcion menu"
        return
    
    if user_states[to] == "esperando opcion menu":
        if "1" == text:
            send_message(to, "No hay parqueaderos disponibles", phone_number_id)
            send_message(to, "🚗 Menú Conductor:\n 1️⃣ Ver parqueaderos disponibles\n 2️⃣ Salir", phone_number_id)
        elif "2" == text:
            send_message(to, "Gracias por usar el servicio!", phone_number_id)
            user_states.pop(to)
        else:
            send_message(to, "Opción invalida", phone_number_id)
    return