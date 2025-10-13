from app.models.whatsapp_webhook import WebhookPayload
from app.logic.send_message import send_message
from app.models.whatsapp_webhook import Message
from app.logic.parqueaderos import obtener_parqueaderos_con_cupos, actualizar_cupos_parqueadero
import app.logic.sesion as sesion

def handle_message(payload: WebhookPayload, db):
    """
    Entrada principal para procesar mensajes
    """
    msg = payload.get_mensaje()
    if not msg or not msg.text:
        return None
    
    usuario = handle_auth(msg, db)
    if not usuario:
        return None
    
    # Solo procesar si el usuario está completamente registrado
    if usuario.estado_registro == "completo":
        handle_user_interaction(msg, usuario, db)
    
    return usuario

def handle_auth(msg: Message, db):
    """
    Maneja autenticación y registro de usuarios
    """
    usuario = sesion.obtener_usuario(msg.from_, db)
    
    # Usuario no existe
    if not usuario:
        return handle_nuevo_usuario(msg.from_, db)
    
    # Usuario existe pero no completó registro
    if usuario.estado_registro != "completo":
        return handle_usuario_nombre(msg, db)
    
    return usuario

def handle_nuevo_usuario(user_id: str, db):
    """
    Inicia el proceso de registro para nuevos usuarios
    """
    sesion.crear_usuario(user_id, db)
    send_message(user_id, "¡Hola! Bienvenido a la plataforma de cupos de parqueaderos!")
    send_message(user_id, "Parece que no estás registrado. Por favor, envía tu nombre para registrarte.")
    sesion.actualizar_estado_registro(user_id, "esperando_nombre", db)
    return None

def handle_usuario_nombre(msg: Message, db):
    """
    Completa el proceso de registro con el nombre del usuario
    """
    usuario = sesion.obtener_usuario(msg.from_, db)
    
    if usuario.estado_registro == "esperando_nombre":
        sesion.actualizar_nombre(msg.from_, msg.text.body, db)
        usuario = sesion.obtener_usuario(msg.from_, db)
        send_message(msg.from_, f"Gracias {usuario.name}, ahora estás registrado. Escribe cualquier mensaje para continuar.")
        sesion.actualizar_estado_registro(msg.from_, "completo", db)
        sesion.actualizar_estado_chat(msg.from_, "inicial", db)
        return usuario
    
    return None

def handle_user_interaction(msg: Message, usuario, db):
    """
    Maneja la interacción principal con usuarios registrados
    """
    text = msg.text.body.lower().strip()
    
    if usuario.estado_chat.paso_actual == "inicial":
        send_message(msg.from_, f"Hola de nuevo {usuario.name} 👋🚘!")
    
    if usuario.rol == "conductor":
        handle_conductor(text, msg.from_, db)
    elif usuario.rol == "gestor_parqueadero":
        handle_gestor(text, msg.from_, db)
    else:
        send_message(msg.from_, "Rol no reconocido. Contacta soporte.")

def handle_conductor(text, user_id, db):
    """
    Maneja el flujo específico para conductores
    """
    usuario = sesion.obtener_usuario(user_id, db)
    current_step = usuario.estado_chat.paso_actual
    
    # Mostrar menú si está en estado inicial o si solicita el menú
    if current_step == "inicial" or text in ["menu", "menú"]:
        mostrar_menu_conductor(user_id, db)
        return
    
    # Procesar opciones del menú
    if current_step == "esperando_opcion_menu":
        handle_conductor_menu_option(text, user_id, db)
        return
    
    # Si no está en ningún flujo específico, mostrar menú
    mostrar_menu_conductor(user_id, db)

def mostrar_menu_conductor(user_id, db):
    """
    Muestra el menú principal para conductores
    """
    
    menu = """🚗 Menú Conductor:
Selecciona una de las siguientes opciones:

1️⃣ Ver parqueaderos disponibles
2️⃣ Suscribirse a notificaciones
3️⃣ Salir

Escribe el número de la opción que deseas:"""
    
    send_message(user_id, menu)
    sesion.actualizar_estado_chat(user_id, "esperando_opcion_menu", db)

def handle_conductor_menu_option(text, user_id, db):
    """
    Procesa las opciones del menú de conductor
    """
    if text == "1":
        handle_ver_parqueaderos(user_id, db)
    elif text == "2":
        handle_suscripcion_notificaciones(user_id, db)
    elif text == "3":
        handle_salir(user_id, db)
    else:
        send_message(user_id, "❌ Opción inválida. Por favor, selecciona 1, 2 o 3.")
        mostrar_menu_conductor(user_id, db)

def handle_ver_parqueaderos(user_id, db):
    """
    Maneja la consulta de parqueaderos disponibles
    """
    send_message(user_id, "🅿️ Consultando parqueaderos disponibles...")
    # Aquí iría la logica para consultar parqueaderos
    parqueaderos = obtener_parqueaderos_con_cupos(db)
    if parqueaderos:
        mensaje = "*Parqueaderos con cupos disponibles:*\n"
        for p in parqueaderos:
            mensaje += f"- *{p.name}* \n  Ubicación: {p.ubicacion} \n  Capacidad: {p.capacidad} \n  Ultima actualización: {p.ultima_actualizacion} \n\n"
        send_message(user_id, mensaje)
    else:
        send_message(user_id, "No hay parqueaderos con cupos disponibles en este momento.")
    mostrar_menu_conductor(user_id, db)

def handle_suscripcion_notificaciones(user_id, db):
    """
    Maneja la suscripción a notificaciones
    """
    send_message(user_id, "🔔 Funcionalidad de suscripción próximamente.")
    mostrar_menu_conductor(user_id, db)

def handle_gestor(text, user_id, db):
    """
    Maneja el flujo específico para gestores de parqueaderos
    """
    usuario = sesion.obtener_usuario(user_id, db)
    current_step = usuario.estado_chat.paso_actual
    
    # Mostrar menú si está en estado inicial o si solicita el menú
    if current_step == "inicial" or text in ["menu", "menú"]:
        mostrar_menu_gestor(user_id, db)
        return
    
    # Procesar opciones del menú
    if current_step == "esperando_opcion_menu":
        handle_gestor_menu_option(text, user_id, db)
        return
    
    if current_step == "esperando_cambio_cupos":
        handle_cupos_gestor(text, user_id, db)
        return
    
    # Si no está en ningún flujo específico, mostrar menú
    mostrar_menu_gestor(user_id, db)
    
def mostrar_menu_gestor(user_id,db):
    """
    Muestra el menu para los gestores de parqueaderos
    """
    menu = """🅿️🚘 Menú Gestor de Parqueaderos:
Selecciona una de las siguientes opciones:

1️⃣ Gestionar cupos libres publicados
2️⃣ Salir

Escribe el número de la opción que deseas:"""
    
    send_message(user_id, menu)
    sesion.actualizar_estado_chat(user_id, "esperando_opcion_menu", db)
    
def handle_gestor_menu_option(text, user_id, db):
    """
    Procesa las opciones del menu de gestor
    """
    if text == "1":
        mostrar_menu_cupos_gestor(user_id, db)
    elif text == "2":
        handle_salir(user_id, db)
    else:
        send_message(user_id, "❌ Opción inválida. Por favor, selecciona 1 o 2.")
        mostrar_menu_gestor(user_id, db)
        
def mostrar_menu_cupos_gestor(user_id, db):
    """
    Muestra el menu para actualizar cupos de los gestores de parqueaderos
    """
    menu = """🅿️🚘 Gestionar cupos del parqueadero:
Selecciona una de las siguientes opciones:

1️⃣ No hay cupo
2️⃣ Hay 1-5 cupos
3️⃣ Hay más de 5 cupos
4️⃣ Volver

Escribe el número de la opción que deseas:"""
    
    send_message(user_id, menu)
    sesion.actualizar_estado_chat(user_id, "esperando_cambio_cupos", db)
    
def handle_cupos_gestor(text, user_id, db):
    """
    Procesa las opciones del menu para actualizar los cupos de un parqueadero
    """
    if text not in "1234":
        send_message(user_id, "❌ Opción inválida. Por favor, selecciona 1, 2, 3 o 4.")
        mostrar_menu_gestor(user_id, db)
        return
    
    cupos_libres = "No hay cupo"
    tiene_cupo = False
    
    if text == "2":
        cupos_libres = "Hay 1-5 cupos"
        tiene_cupo = True
    elif text == "3":
        cupos_libres = "Hay más de 5 cupos"
        tiene_cupo = True
    if text != "4":
        exito = actualizar_cupos_parqueadero(user_id, cupos_libres, tiene_cupo, db)
        
        if exito:
            send_message(user_id, "Se actualizaron los cupos del parqueadero 😀")
        else:
            send_message(user_id, "Ocurrió un error, inténtalo de nuevo")
            
    mostrar_menu_gestor(user_id, db)
        
def handle_salir(user_id, db):
    """
    Maneja la salida del usuario
    """
    send_message(user_id, "👋 ¡Gracias por usar el servicio! Escribe cualquier mensaje para volver.")
    sesion.actualizar_estado_chat(user_id, "inicial", db)