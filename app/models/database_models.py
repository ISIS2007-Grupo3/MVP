import uuid
from pydantic import BaseModel, Field
from typing import Optional

class EstadoChat(BaseModel):
    ultima_interaccion: Optional[str] = None  # Timestamp de la última interacción
    paso_actual: Optional[str] = None  # Paso actual en el flujo de conversación
    contexto_temporal: Optional[dict] = None  # Para guardar datos temporales durante flujos

class Parqueadero(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str 
    ubicacion: str
    capacidad: int
    tiene_cupos: bool = True
    cupos_libres: str = "0"  # Valor por defecto
    ultima_actualizacion: Optional[str] = None
    class Config:
        allow_population_by_field_name = True

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")  # MongoDB usa _id como clave primaria
    name: Optional[str] = None
    rol: Optional[str] = None  # "conductor" o "gestor_parqueadero"
    estado_chat: EstadoChat = EstadoChat()
    estado_registro: Optional[str] = None  # "esperando_nombre", "completo", etc.
    class Config:
        allow_population_by_field_name = True  # Permite usar "id" y "_id" indistintamente

class Conductor(User):
    cosas: Optional[str] = None


class GestorParqueadero(User):
    parqueadero_id: Optional[str] = None  # ID del parqueadero que gestiona

class Suscripcion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    conductor_id: str  # WhatsApp ID del conductor
    parqueadero_id: Optional[str] = None  # Si es None, está suscrito a todos los parqueaderos
    fecha_suscripcion: Optional[str] = None
    activa: bool = True
    
    class Config:
        allow_population_by_field_name = True