from app.logic.send_message import send_message
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.utils.tiempo_utils import formatear_tiempo_para_usuario
from app.services.whatsapp_interactive_service import WhatsAppInteractiveService
from typing import List

class WhatsAppMessageService:
    """
    Servicio para manejar todos los mensajes de WhatsApp
    Centraliza la lógica de creación y envío de mensajes
    """
    
    def __init__(self, db=None):
        self.db = db
        self.interactive_service = WhatsAppInteractiveService()
    
    # ===== MENSAJES DE BIENVENIDA Y REGISTRO =====
    
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
    
    # ===== MENÚS =====
    
    def mostrar_menu_conductor(self, user_id: str):
        """Muestra el menú principal para conductores usando mensajes interactivos"""
        success = self.interactive_service.send_conductor_menu(user_id)
        if not success:
            # Fallback al mensaje de texto tradicional
            menu = """🚗 *Menú Conductor*

Bienvenido al sistema de parqueaderos. Escribe el número de tu opción:

1️⃣ Ver Parqueaderos
   📍 Consulta parqueaderos con cupos disponibles

2️⃣ Notificaciones  
   🔔 Gestiona tus suscripciones de alertas

3️⃣ Salir
   👋 Cerrar sesión del sistema"""
            send_message(user_id, menu)
    
    def mostrar_menu_suscripciones(self, user_id: str):
        """Muestra el menú de opciones de suscripción usando mensajes interactivos"""
        success = self.interactive_service.send_subscription_menu(user_id)
        if not success:
            # Fallback al mensaje de texto tradicional
            menu = """🔔 *Notificaciones de Parqueaderos*

Gestiona tus suscripciones de notificaciones. Escribe el número de tu opción:

1️⃣ Todos los parqueaderos
   🌐 Recibe notificaciones de todos

2️⃣ Parqueadero específico
   🅿️ Elige un parqueadero particular

3️⃣ Ver mis suscripciones
   📋 Revisa tus suscripciones actuales

4️⃣ Desuscribir todo
   ❌ Cancelar todas las notificaciones

5️⃣ Volver al menú
   ⬅️ Regresar al menú principal"""
            send_message(user_id, menu)
    
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
    
    # ===== MENSAJES DE PARQUEADEROS =====
    
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
        """Muestra información detallada de un parqueadero"""
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
    
    # ===== MENSAJES DE SUSCRIPCIONES =====
    
    def confirmar_suscripcion_global(self, user_id: str):
        """Confirma suscripción a todos los parqueaderos"""
        send_message(user_id, "✅ Te has suscrito a notificaciones de *todos* los parqueaderos!")
    
    def confirmar_suscripcion_especifica(self, user_id: str, nombre_parqueadero: str):
        """Confirma suscripción a un parqueadero específico"""
        send_message(user_id, f"🔔 Te has suscrito a notificaciones del parqueadero: *{nombre_parqueadero}*")
    
    def confirmar_desuscripcion_total(self, user_id: str):
        """Confirma desuscripción de todas las notificaciones"""
        send_message(user_id, "✅ Te has desuscrito de todas las notificaciones correctamente.")
    
    def confirmar_desuscripcion_especifica(self, user_id: str, nombre_parqueadero: str):
        """Confirma desuscripción de un parqueadero específico"""
        send_message(user_id, f"❌ Te has desuscrito del parqueadero: *{nombre_parqueadero}*")
    
    def mostrar_suscripciones_actuales(self, user_id: str, suscripciones: List) -> bool:
        """Muestra las suscripciones actuales del conductor con menú interactivo"""
        print(f"🔍 mostrar_suscripciones_actuales: {len(suscripciones) if suscripciones else 0} suscripciones")
        if suscripciones:
            # Intentar mostrar menú interactivo
            success = self.interactive_service.send_subscriptions_list_with_unsubscribe(user_id, suscripciones)
            print(f"📊 Resultado del servicio interactivo: {success}")
            if success:
                return True
            
            # Fallback a mensaje de texto
            mensaje = "*Tus suscripciones actuales:*\n\n"
            for i, suscripcion in enumerate(suscripciones, 1):
                if suscripcion["tipo"] == "global":
                    mensaje += f"{i}️⃣ 🌐 Todos los parqueaderos\n"
                else:
                    mensaje += f"{i}️⃣ 🅿️ {suscripcion['parqueadero']}\n"
                mensaje += f"   📅 Desde: {formatear_tiempo_para_usuario(suscripcion['fecha'])}\n\n"
            
            mensaje += "Para desuscribirte, usa el menú de notificaciones ➡️ Opción ❌ Desuscribirme"
        else:
            mensaje = "❌ No tienes suscripciones activas"
        
        send_message(user_id, mensaje)
        return False
    
    # ===== NOTIFICACIONES =====
    
    def crear_notificacion_cupo_liberado(self, parqueadero) -> str:
        """Crea el mensaje de notificación cuando se libera un cupo"""
        # Usar rango si está disponible, sino usar cupos_libres tradicional
        info_cupos = parqueadero.rango_cupos or f"~{parqueadero.cupos_libres} cupos"
        estado = parqueadero.estado_ocupacion or "Cupos disponibles"
        
        return f"""🚗 ¡CUPO DISPONIBLE! 🅿️

📍 *{parqueadero.name}*
📌 Ubicación: {parqueadero.ubicacion}
📊 Estado: {estado}
🅿️ Disponibilidad: {info_cupos}

¡Apúrate antes de que se agote!

Para desuscribirte, escribe "desuscribir" """
    
    def enviar_notificacion_cupo(self, user_id: str, mensaje: str):
        """Envía una notificación de cupo liberado"""
        send_message(user_id, mensaje)
    
    # ===== MENSAJES DE ERROR Y VALIDACIÓN =====
    
    def error_opcion_invalida_menu_principal(self, user_id: str):
        """Error cuando selecciona opción inválida en menú principal"""
        send_message(user_id, "❌ Opción no reconocida. Por favor, selecciona una opción del menú:")
    
    def error_opcion_invalida_suscripciones(self, user_id: str):
        """Error cuando selecciona opción inválida en menú de suscripciones"""
        send_message(user_id, "❌ Opción no válida. Por favor, selecciona del menú de suscripciones:")
    
    def error_numero_invalido(self, user_id: str):
        """Error cuando envía un número inválido"""
        send_message(user_id, "❌ Número no válido. Por favor, selecciona una opción del menú:")
    
    def error_parqueadero_no_encontrado(self, user_id: str):
        """Error cuando no se encuentra el parqueadero"""
        send_message(user_id, "❌ Parqueadero no encontrado. Intenta de nuevo:")
    
    def error_sin_suscripciones(self, user_id: str):
        """Error cuando no tiene suscripciones activas"""
        send_message(user_id, "ℹ️ No tienes suscripciones activas en este momento.")
    
    def error_suscripcion_general(self, user_id: str, mensaje_error: str):
        """Error general en suscripciones"""
        send_message(user_id, f"❌ Error: {mensaje_error}")
    
    def confirmar_desuscripcion_total(self, user_id: str):
        """Confirma desuscripción de todas las notificaciones"""
        send_message(user_id, "✅ Te has desuscrito de todas las notificaciones correctamente")
    
    def confirmar_desuscripcion_parqueadero(self, user_id: str, nombre_parqueadero: str):
        """Confirma desuscripción de un parqueadero específico"""
        send_message(user_id, f"✅ Te has desuscrito de '{nombre_parqueadero}' correctamente")
    
    def error_rol_no_reconocido(self, user_id: str):
        """Error cuando el rol del usuario no es reconocido"""
        send_message(user_id, "❌ Rol no reconocido. Por favor contacta al soporte técnico.")
    
    # ===== MENSAJES DE ACTUALIZACIÓN DE CUPOS =====
    
    def solicitar_cupos_actualizacion(self, user_id: str):
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
    
    def confirmar_actualizacion_cupos(self, user_id: str, cupos_libres: str, notificaciones_enviadas: int):
        """Confirma la actualización de cupos"""
        mensaje = f"""✅ *Cupos actualizados exitosamente*

🅿️ Cupos libres: {cupos_libres}
📢 Notificaciones enviadas: {notificaciones_enviadas}"""
        send_message(user_id, mensaje)
    
    def confirmar_actualizacion_cupos_con_descripcion(self, user_id: str, descripcion: str, cupos_libres: str, notificaciones_enviadas: int):
        """Confirma la actualización de cupos con descripción del estado"""
        mensaje = f"""✅ *Cupos actualizados exitosamente*

📋 *Estado:* {descripcion}
🅿️ *Cupos aproximados:* {cupos_libres}
📢 *Notificaciones enviadas:* {notificaciones_enviadas}

{self._obtener_emoji_notificaciones(notificaciones_enviadas)}"""
        send_message(user_id, mensaje)
    
    def _obtener_emoji_notificaciones(self, cantidad: int) -> str:
        """Obtiene emoji apropiado según cantidad de notificaciones enviadas"""
        if cantidad == 0:
            return "ℹ️ No hay conductores suscritos actualmente"
        elif cantidad == 1:
            return "👤 Se notificó a 1 conductor"
        elif cantidad <= 5:
            return f"👥 Se notificó a {cantidad} conductores"
        else:
            return f"🚨 Se notificó a {cantidad} conductores - ¡Alto interés!"
    
    def error_formato_cupos(self, user_id: str):
        """Error en formato de actualización de cupos"""
        send_message(user_id, "❌ Opción no válida. Por favor, selecciona del menú de actualización:")
    
    def mostrar_ayuda_cupos(self, user_id: str):
        """Muestra ayuda detallada sobre las opciones de cupos"""
        mensaje = """ℹ️ *Guía de Opciones de Cupos*

🔴 *Opción 1 - Parqueadero lleno:*
   • No hay espacios disponibles
   • No se envían notificaciones

🟡 *Opción 2 - Pocos cupos:*
   • Entre 1-5 espacios disponibles
   • Ideal para ocupación alta

🟢 *Opción 3 - Algunos cupos:*
   • Entre 6-15 espacios disponibles  
   • Ocupación media-alta

🟢 *Opción 4 - Muchos cupos:*
   • Entre 16-30 espacios disponibles
   • Ocupación media-baja

🔵 *Opción 5 - Casi vacío:*
   • Más de 30 espacios disponibles
   • Ocupación muy baja

💡 *Las opciones 2-5 activarán notificaciones automáticas a conductores suscritos*"""
        send_message(user_id, mensaje)
    
    # ===== MENSAJES DE DESPEDIDA =====
    
    def despedir_usuario(self, user_id: str):
        """Despide al usuario al salir"""
        send_message(user_id, "👋 ¡Gracias por usar el servicio! Escribe cualquier mensaje para volver.")
    
    # ===== MENSAJES DE COMANDOS DE DESUSCRIPCIÓN =====
    
    def mostrar_ayuda_desuscripcion(self, user_id: str, suscripciones: List):
        """Muestra ayuda para comandos de desuscripción"""
        mensaje = "*Tus suscripciones actuales:*\n\n"
        for i, suscripcion in enumerate(suscripciones, 1):
            if suscripcion["tipo"] == "global":
                mensaje += f"{i}️⃣ 🌐 Todos los parqueaderos\n"
            else:
                mensaje += f"{i}️⃣ 🅿️ {suscripcion['parqueadero']}\n"
        
        mensaje += "\nEscribe 'desuscribir todo' o 'desuscribir [número]' para desuscribirte"
        send_message(user_id, mensaje)
    
    def error_comando_desuscripcion(self, user_id: str):
        """Error en comando de desuscripción"""
        send_message(user_id, "❌ Comando inválido. Usa 'desuscribir', 'desuscribir todo' o 'desuscribir [número]'")
    
    def informar_desuscripcion_especifica_limitada(self, user_id: str):
        """Informa sobre limitación de desuscripción específica"""
        send_message(user_id, "Para desuscribirte de parqueaderos específicos, usa el menú de suscripciones")
    
    # ===== MENSAJE CONSULTANDO =====
    
    def mostrar_consultando_parqueaderos(self, user_id: str):
        """Mensaje mientras consulta parqueaderos"""
        send_message(user_id, "🅿️ Consultando parqueaderos disponibles...")
    
    # ===== MENSAJES DE CONFIRMACIÓN DE CUPOS =====
    
    def solicitar_confirmacion_cupos(self, user_id: str, opcion: int, descripcion: str, rango: str):
        """Solicita confirmación antes de actualizar los cupos usando mensajes interactivos"""
        success = self.interactive_service.send_confirmation_cupos(user_id, descripcion, rango)
        if not success:
            # Fallback al mensaje de texto tradicional con formato descriptivo
            mensaje = f"""⚠️ *Confirmar Actualización*

Verifica que la información sea correcta:

📋 *Estado:* {descripcion}
🅿️ *Disponibilidad:* {rango}

Escribe el número de tu opción para confirmar:

✅ *1* - Confirmar actualización
   • Guardar cambios y notificar a conductores suscritos

🔄 *2* - Cambiar selección
   • Volver atrás para elegir otro estado

❌ *3* - Cancelar operación
   • Descartar cambios y volver al menú principal

💡 *Tip: Los conductores recibirán notificación si hay cupos disponibles*"""
            send_message(user_id, mensaje)
    
    def error_confirmacion_cupos(self, user_id: str):
        """Error en la confirmación de cupos"""
        send_message(user_id, "❌ Opción no válida. Por favor, selecciona una opción del menú de confirmación:")