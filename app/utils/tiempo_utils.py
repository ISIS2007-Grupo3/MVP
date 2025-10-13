"""
Utilidades para manejo de fechas y tiempo con zona horaria de Bogotá
"""
from datetime import datetime
import pytz

def obtener_tiempo_bogota() -> str:
    """
    Obtiene el tiempo actual en la zona horaria de Bogotá
    Returns:
        str: Timestamp en formato "YYYY-MM-DD HH:MM:SS" en zona horaria de Bogotá
    """
    zona_bogota = pytz.timezone('America/Bogota')
    tiempo_actual = datetime.now(zona_bogota)
    return tiempo_actual.strftime("%Y-%m-%d %H:%M:%S")

def obtener_tiempo_bogota_formato(formato: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Obtiene el tiempo actual en la zona horaria de Bogotá con formato personalizado
    Args:
        formato (str): Formato del timestamp (por defecto: "%Y-%m-%d %H:%M:%S")
    Returns:
        str: Timestamp formateado en zona horaria de Bogotá
    """
    zona_bogota = pytz.timezone('America/Bogota')
    tiempo_actual = datetime.now(zona_bogota)
    return tiempo_actual.strftime(formato)

def obtener_fecha_bogota() -> str:
    """
    Obtiene solo la fecha actual en la zona horaria de Bogotá
    Returns:
        str: Fecha en formato "YYYY-MM-DD"
    """
    return obtener_tiempo_bogota_formato("%Y-%m-%d")

def obtener_hora_bogota() -> str:
    """
    Obtiene solo la hora actual en la zona horaria de Bogotá
    Returns:
        str: Hora en formato "HH:MM:SS"
    """
    return obtener_tiempo_bogota_formato("%H:%M:%S")

def formatear_tiempo_para_usuario(timestamp: str) -> str:
    """
    Formatea un timestamp para mostrar al usuario de manera más legible
    Args:
        timestamp (str): Timestamp en formato "YYYY-MM-DD HH:MM:SS"
    Returns:
        str: Timestamp formateado para el usuario
    """
    try:
        # Parsear el timestamp
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        # Formatear para mostrar al usuario (más legible)
        return dt.strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return timestamp or "N/A"