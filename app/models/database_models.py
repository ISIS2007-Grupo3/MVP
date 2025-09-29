from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")  # MongoDB usa _id como clave primaria
    name: str
    rol: str  # "conductor" o "gestor_parqueadero"

    class Config:
        allow_population_by_field_name = True  # Permite usar "id" y "_id" indistintamente

class Conductor(User):
    cosas: Optional[str] = None

class Parqueadero(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    ubicacion: str
    capacidad: int

    class Config:
        allow_population_by_field_name = True

class GestorParqueadero(User):
    parqueadero: Parqueadero