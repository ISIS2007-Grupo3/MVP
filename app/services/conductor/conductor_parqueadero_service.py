"""
Servicio especializado para consulta de parqueaderos por conductores
"""
from app.services.message.mensaje_parqueadero_service import MensajeParqueaderoService
from app.services.message.mensaje_error_service import MensajeErrorService
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.logic.parqueaderos import obtener_parqueaderos_con_cupos
import app.logic.sesion as sesion


class ConductorParqueaderoService:
    """
    Servicio enfocado en consulta y visualización de parqueaderos.
    Responsabilidad: Mostrar parqueaderos disponibles y sus detalles.
    """
    
    def __init__(self, db):
        self.db = db
        self.mensaje_parqueadero_service = MensajeParqueaderoService(db)
        self.mensaje_error_service = MensajeErrorService()
        self.parqueadero_repo = ParqueaderoRepository(db)
    
    def consultar_parqueaderos(self, user_id: str, pagina: int = 1):
        """Muestra parqueaderos con cupos disponibles con detalles y paginación"""
        self.mensaje_parqueadero_service.mostrar_consultando_parqueaderos(user_id)
        parqueaderos = obtener_parqueaderos_con_cupos(self.db)
        
        if parqueaderos:
            # Enviar lista interactiva con opción de ver detalles y paginación
            success = self.mensaje_parqueadero_service.mostrar_parqueaderos_interactivos(user_id, parqueaderos, pagina)
            
            if success:
                # Guardar IDs de parqueaderos y página actual en contexto para referencia
                parqueaderos_ids = [p.id for p in parqueaderos]
                sesion.actualizar_contexto_temporal(user_id, {
                    "parqueaderos_consulta": parqueaderos_ids,
                    "pagina_actual": pagina
                }, self.db)
                sesion.actualizar_estado_chat(user_id, "viendo_parqueaderos", self.db)
                return {"success": True, "modo": "interactivo"}
            else:
                # Fallback: mostrar solo texto
                self.mensaje_parqueadero_service.mostrar_parqueaderos_disponibles(user_id, parqueaderos)
                return {"success": True, "modo": "texto"}
        else:
            self.mensaje_parqueadero_service.mostrar_parqueaderos_disponibles(user_id, parqueaderos)
            return {"success": True, "modo": "vacio"}
    
    def seleccionar_parqueadero_detalles(self, text: str, user_id: str) -> dict:
        """
        Maneja la selección de un parqueadero para ver detalles o navegación de páginas
        
        Returns:
            dict con: {"action": str, "success": bool, "pagina": int}
            action puede ser: "volver_menu", "pagina_anterior", "pagina_siguiente", "ver_detalle", "error"
        """
        try:
            # Obtener contexto actual
            usuario = sesion.obtener_usuario(user_id, self.db)
            contexto_temporal = usuario.estado_chat.contexto_temporal or {}
            parqueaderos_ids = contexto_temporal.get('parqueaderos_consulta', [])
            pagina_actual = contexto_temporal.get('pagina_actual', 1)
            
            # Manejar opción de volver
            if text == "volver_menu_conductor":
                return {"action": "volver_menu", "success": True}
            
            # Manejar navegación de páginas (anterior)
            if text.startswith("pagina_anterior_"):
                nueva_pagina = int(text.split("_")[2])
                return {"action": "pagina_anterior", "success": True, "pagina": nueva_pagina}
            
            # Manejar navegación de páginas (siguiente)
            if text.startswith("pagina_siguiente_"):
                nueva_pagina = int(text.split("_")[2])
                return {"action": "pagina_siguiente", "success": True, "pagina": nueva_pagina}
            
            # Manejar selección interactiva de parqueadero
            if text.startswith("detalle_parqueadero_"):
                index = int(text.split("_")[2])
                
                if 0 <= index < len(parqueaderos_ids):
                    parqueadero_id = parqueaderos_ids[index]
                    parqueadero = self.parqueadero_repo.find_by_id(parqueadero_id)
                    
                    if parqueadero:
                        self.mensaje_parqueadero_service.mostrar_detalle_parqueadero(user_id, parqueadero)
                        return {"action": "ver_detalle", "success": True, "pagina": pagina_actual}
                    else:
                        self.mensaje_error_service.error_parqueadero_no_encontrado(user_id)
                        return {"action": "error", "success": False, "pagina": pagina_actual}
                else:
                    self.mensaje_error_service.error_numero_invalido(user_id)
                    return {"action": "error", "success": False, "pagina": pagina_actual}
            
                # Si no coincide con ninguna opción interactiva
            self.mensaje_error_service.error_numero_invalido(user_id)
            return {"action": "error", "success": False, "pagina": pagina_actual}
                
        except ValueError:
            usuario = sesion.obtener_usuario(user_id, self.db)
            contexto_temporal = usuario.estado_chat.contexto_temporal or {}
            pagina_actual = contexto_temporal.get('pagina_actual', 1)
            self.mensaje_error_service.error_numero_invalido(user_id)
            return {"action": "error", "success": False, "pagina": pagina_actual}
        except Exception as e:
            print(f"Error en selección de parqueadero: {e}")
            import traceback
            traceback.print_exc()
            self.mensaje_error_service.error_suscripcion_general(user_id, "Error al consultar parqueadero")
            return {"action": "error", "success": False}
