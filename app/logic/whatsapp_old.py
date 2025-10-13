from app.models.whatsapp_webhook import WebhookPayload, Message
from app.services.whatsapp_message_service import WhatsAppMessageService
from app.services.whatsapp_flow_service import WhatsAppFlowService
import app.logic.sesion as sesion

def handle_message(payload: WebhookPayload, db):
    """
    Entrada principal para procesar mensajes
    """
    msg = payload.get_mensaje()
    if not msg or not msg.text:
        return None
    
    # Inicializar servicios
    message_service = WhatsAppMessageService(db)
    flow_service = WhatsAppFlowService(db)
    
    usuario = handle_auth(msg, db, message_service)
    if not usuario:
        return None
    
    # Solo procesar si el usuario está completamente registrado
    if usuario.estado_registro == "completo":
        handle_user_interaction(msg, usuario, db, message_service, flow_service)
    
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
    
    # Comandos especiales que funcionan en cualquier momento
    if text.lower().startswith("desuscribir"):
        handle_desuscribir_comando(text, user_id, db)
        return
    
    # Mostrar menú si está en estado inicial o si solicita el menú
    if current_step == "inicial" or text in ["menu", "menú"]:
        mostrar_menu_conductor(user_id, db)
        return
    
    # Procesar opciones del menú principal
    if current_step == "esperando_opcion_menu":
        handle_conductor_menu_option(text, user_id, db)
        return
    
    # Procesar opciones del menú de suscripciones
    if current_step == "esperando_opcion_suscripcion":
        handle_suscripcion_menu_option(text, user_id, db)
        return
    
    # Procesar selección de parqueadero para suscripción
    if current_step == "esperando_seleccion_parqueadero":
        handle_seleccion_parqueadero_suscripcion(text, user_id, db)
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
    send_message(user_id, """🔔 *Notificaciones de Parqueaderos*

Selecciona una opción:

1️⃣ Suscribirme a todos los parqueaderos
2️⃣ Ver parqueaderos para suscripción específica
3️⃣ Ver mis suscripciones actuales
4️⃣ Desuscribirme de todas las notificaciones
5️⃣ Volver al menú principal

Escribe el número de tu opción:""")
    
    sesion.actualizar_estado_chat(user_id, "esperando_opcion_suscripcion", db)

def handle_suscripcion_menu_option(text, user_id, db):
    """
    Procesa las opciones del menú de suscripciones
    """
    notification_service = NotificationService(db)
    
    if text == "1":
        # Suscribirse a todos los parqueaderos
        result = notification_service.suscribir_conductor(user_id, None)
        if result["success"]:
            send_message(user_id, "✅ Te has suscrito a notificaciones de *todos* los parqueaderos!")
        else:
            send_message(user_id, f"❌ Error: {result['message']}")
        mostrar_menu_conductor(user_id, db)
        
    elif text == "2":
        # Mostrar parqueaderos para suscripción específica
        mostrar_parqueaderos_para_suscripcion(user_id, db)
        
    elif text == "3":
        # Ver suscripciones actuales
        mostrar_suscripciones_actuales(user_id, db)
        
    elif text == "4":
        # Desuscribirse de todas
        result = notification_service.desuscribir_conductor(user_id, None)
        if result["success"]:
            send_message(user_id, "❌ Te has desuscrito de todas las notificaciones")
        else:
            send_message(user_id, f"❌ Error: {result['message']}")
        mostrar_menu_conductor(user_id, db)
        
    elif text == "5":
        # Volver al menú principal
        mostrar_menu_conductor(user_id, db)
        
    else:
        send_message(user_id, "❌ Opción inválida. Por favor, selecciona 1, 2, 3, 4 o 5.")
        handle_suscripcion_notificaciones(user_id, db)

def mostrar_parqueaderos_para_suscripcion(user_id, db):
    """
    Muestra los parqueaderos disponibles para suscripción
    """
    from app.repositories.parqueadero_repository import ParqueaderoRepository
    parqueadero_repo = ParqueaderoRepository(db)
    parqueaderos = parqueadero_repo.find_all()
    
    if parqueaderos:
        mensaje = "*Parqueaderos disponibles:*\n\n"
        for i, p in enumerate(parqueaderos, 1):
            mensaje += f"{i}️⃣ *{p.name}*\n   📍 {p.ubicacion}\n\n"
        mensaje += f"{len(parqueaderos) + 1}️⃣ Volver al menú de suscripciones\n\n"
        mensaje += "Escribe el número del parqueadero al que te quieres suscribir:"
        
        send_message(user_id, mensaje)
        
        # Guardar lista de parqueaderos en sesión para referencia
        sesion.actualizar_contexto_temporal(user_id, {"parqueaderos": [p.id for p in parqueaderos]}, db)
        sesion.actualizar_estado_chat(user_id, "esperando_seleccion_parqueadero", db)
    else:
        send_message(user_id, "❌ No hay parqueaderos disponibles")
        handle_suscripcion_notificaciones(user_id, db)

def handle_seleccion_parqueadero_suscripcion(text, user_id, db):
    """
    Maneja la selección de parqueadero para suscripción
    """
    try:
        opcion = int(text)
        usuario = sesion.obtener_usuario(user_id, db)
        contexto = getattr(usuario.estado_chat, 'contexto_temporal', {})
        parqueaderos_ids = contexto.get('parqueaderos', [])
        
        if opcion == len(parqueaderos_ids) + 1:
            # Volver al menú de suscripciones
            handle_suscripcion_notificaciones(user_id, db)
            return
            
        if 1 <= opcion <= len(parqueaderos_ids):
            parqueadero_id = parqueaderos_ids[opcion - 1]
            notification_service = NotificationService(db)
            result = notification_service.suscribir_conductor(user_id, parqueadero_id)
            
            if result["success"]:
                send_message(user_id, "✅ ¡Suscripción exitosa! Recibirás notificaciones cuando haya cupos disponibles.")
            else:
                send_message(user_id, f"❌ Error: {result['message']}")
        else:
            send_message(user_id, "❌ Opción inválida")
            
    except ValueError:
        send_message(user_id, "❌ Por favor, envía un número válido")
    
    mostrar_menu_conductor(user_id, db)

def mostrar_suscripciones_actuales(user_id, db):
    """
    Muestra las suscripciones actuales del conductor
    """
    notification_service = NotificationService(db)
    suscripciones = notification_service.listar_suscripciones_conductor(user_id)
    
    if suscripciones:
        mensaje = "*Tus suscripciones actuales:*\n\n"
        for i, suscripcion in enumerate(suscripciones, 1):
            if suscripcion["tipo"] == "global":
                mensaje += f"{i}️⃣ 🌐 Todos los parqueaderos\n"
            else:
                mensaje += f"{i}️⃣ 🅿️ {suscripcion['parqueadero']}\n"
            mensaje += f"   📅 Desde: {suscripcion['fecha']}\n\n"
        
        mensaje += "Para desuscribirte, escribe 'desuscribir' seguido del número o 'desuscribir todo'"
    else:
        mensaje = "❌ No tienes suscripciones activas"
    
    send_message(user_id, mensaje)
    mostrar_menu_conductor(user_id, db)

def handle_desuscribir_comando(text, user_id, db):
    """
    Maneja comandos de desuscripción desde cualquier punto de la conversación
    Ejemplos: "desuscribir", "desuscribir todo", "desuscribir 1"
    """
    notification_service = NotificationService(db)
    
    # Limpiar el comando y extraer parámetros
    comando_parts = text.lower().split()
    
    if len(comando_parts) == 1:  # Solo "desuscribir"
        # Mostrar suscripciones actuales para que elija
        suscripciones = notification_service.listar_suscripciones_conductor(user_id)
        
        if not suscripciones:
            send_message(user_id, "❌ No tienes suscripciones activas")
            return
            
        mensaje = "*Tus suscripciones actuales:*\n\n"
        for i, suscripcion in enumerate(suscripciones, 1):
            if suscripcion["tipo"] == "global":
                mensaje += f"{i}️⃣ 🌐 Todos los parqueaderos\n"
            else:
                mensaje += f"{i}️⃣ 🅿️ {suscripcion['parqueadero']}\n"
        
        mensaje += "\nEscribe 'desuscribir todo' o 'desuscribir [número]' para desuscribirte"
        send_message(user_id, mensaje)
        
    elif len(comando_parts) == 2:
        if comando_parts[1] == "todo":
            # Desuscribir de todo
            result = notification_service.desuscribir_conductor(user_id, None)
            send_message(user_id, "✅ Te has desuscrito de todas las notificaciones")
        else:
            try:
                # Desuscribir de suscripción específica por número
                numero = int(comando_parts[1])
                suscripciones = notification_service.listar_suscripciones_conductor(user_id)
                
                if 1 <= numero <= len(suscripciones):
                    # Aquí necesitarías más lógica para identificar el parqueadero específico
                    # Por simplicidad, desuscribir de todo si es global
                    suscripcion = suscripciones[numero - 1]
                    if suscripcion["tipo"] == "global":
                        result = notification_service.desuscribir_conductor(user_id, None)
                        send_message(user_id, "✅ Te has desuscrito de las notificaciones globales")
                    else:
                        send_message(user_id, "Para desuscribirte de parqueaderos específicos, usa el menú de suscripciones")
                else:
                    send_message(user_id, "❌ Número de suscripción inválido")
            except ValueError:
                send_message(user_id, "❌ Comando inválido. Usa 'desuscribir todo' o 'desuscribir [número]'")
    else:
        send_message(user_id, "❌ Comando inválido. Usa 'desuscribir', 'desuscribir todo' o 'desuscribir [número]'")

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