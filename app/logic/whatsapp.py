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

def handle_auth(msg: Message, db, message_service: WhatsAppMessageService):
    """
    Maneja autenticación y registro de usuarios
    """
    usuario = sesion.obtener_usuario(msg.from_, db)
    
    # Usuario no existe
    if not usuario:
        return handle_nuevo_usuario(msg.from_, db, message_service)
    
    # Usuario existe pero no completó registro
    if usuario.estado_registro != "completo":
        return handle_usuario_nombre(msg, db, message_service)
    
    return usuario

def handle_nuevo_usuario(user_id: str, db, message_service: WhatsAppMessageService):
    """
    Inicia el proceso de registro para nuevos usuarios
    """
    sesion.crear_usuario(user_id, db)
    message_service.enviar_bienvenida(user_id)
    message_service.solicitar_nombre(user_id)
    sesion.actualizar_estado_registro(user_id, "esperando_nombre", db)
    return None

def handle_usuario_nombre(msg: Message, db, message_service: WhatsAppMessageService):
    """
    Completa el proceso de registro con el nombre del usuario
    """
    usuario = sesion.obtener_usuario(msg.from_, db)
    
    if usuario.estado_registro == "esperando_nombre":
        sesion.actualizar_nombre(msg.from_, msg.text.body, db)
        usuario = sesion.obtener_usuario(msg.from_, db)
        message_service.confirmar_registro(msg.from_, usuario.name)
        sesion.actualizar_estado_registro(msg.from_, "completo", db)
        sesion.actualizar_estado_chat(msg.from_, "inicial", db)
        return usuario
    
    return None

def handle_user_interaction(msg: Message, usuario, db, message_service: WhatsAppMessageService, flow_service: WhatsAppFlowService):
    """
    Maneja la interacción principal con usuarios registrados
    """
    text = msg.text.body.lower().strip()
    
    if usuario.estado_chat.paso_actual == "inicial":
        message_service.saludar_usuario_registrado(msg.from_, usuario.name)
    
    if usuario.rol == "conductor":
        handle_conductor(text, msg.from_, db, flow_service)
    elif usuario.rol == "gestor_parqueadero":
        handle_gestor(text, msg.from_, db, flow_service)
    else:
        message_service.error_rol_no_reconocido(msg.from_)

def handle_conductor(text: str, user_id: str, db, flow_service: WhatsAppFlowService):
    """
    Maneja el flujo específico para conductores
    """
    usuario = sesion.obtener_usuario(user_id, db)
    current_step = usuario.estado_chat.paso_actual
    
    # Comandos especiales que funcionan en cualquier momento
    if text.lower().startswith("desuscribir"):
        flow_service.handle_desuscribir_comando(text, user_id)
        return
    
    # Mostrar menú si está en estado inicial o si solicita el menú
    if current_step == "inicial" or text in ["menu", "menú"]:
        flow_service.mostrar_menu_conductor(user_id)
        return
    
    # Procesar opciones del menú principal
    if current_step == "esperando_opcion_menu":
        flow_service.handle_conductor_menu_option(text, user_id)
        return
    
    # Procesar opciones del menú de suscripciones
    if current_step == "esperando_opcion_suscripcion":
        flow_service.handle_suscripcion_menu_option(text, user_id)
        return
    
    # Procesar selección de parqueadero para suscripción
    if current_step == "esperando_seleccion_parqueadero":
        flow_service.handle_seleccion_parqueadero_suscripcion(text, user_id)
        return
    
    # Si no está en ningún flujo específico, mostrar menú
    flow_service.mostrar_menu_conductor(user_id)

def handle_gestor(text: str, user_id: str, db, flow_service: WhatsAppFlowService):
    """
    Maneja el flujo específico para gestores de parqueaderos
    """
    usuario = sesion.obtener_usuario(user_id, db)
    current_step = usuario.estado_chat.paso_actual
    
    # Mostrar menú si está en estado inicial o si solicita el menú
    if current_step == "inicial" or text in ["menu", "menú"]:
        flow_service.mostrar_menu_gestor(user_id)
        return
    
    # Procesar opciones del menú
    if current_step == "esperando_opcion_menu":
        flow_service.handle_gestor_menu_option(text, user_id)
        return
    
    if current_step == "esperando_cambio_cupos":
        flow_service.handle_cupos_gestor(text, user_id)
        return
    
    if current_step == "esperando_confirmacion_cupos":
        flow_service.handle_cupos_gestor(text, user_id)
        return
    
    # Si no está en ningún flujo específico, mostrar menú
    flow_service.mostrar_menu_gestor(user_id)