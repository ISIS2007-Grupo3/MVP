from app.repositories.user_repositories import UserRepository, ConductorRepository
from app.models.database_models import Conductor, User

def obtener_usuario(wa_id: str, db) -> User:
    repo = UserRepository(db)
    return repo.find_by_id(wa_id)

def crear_usuario(wa_id: str, db):
    repo = ConductorRepository(db)
    nuevo_usuario = repo.create(Conductor(_id=wa_id, rol="conductor"))
    return nuevo_usuario

def actualizar_nombre(wa_id: str, nombre: str, db):
    repo = UserRepository(db)
    usuario_actualizado = repo.actualizar_nombre(wa_id, nombre)
    return usuario_actualizado

def actualizar_estado_chat(wa_id: str, paso_actual: str, db):
    repo = UserRepository(db)
    usuario_actualizado = repo.actualizar_estado_chat(wa_id, paso_actual)
    return usuario_actualizado

def actualizar_estado_registro(wa_id: str, estado_registro: str, db):
    repo = UserRepository(db)
    usuario_actualizado = repo.actualizar_estado_registro(wa_id, estado_registro)
    return usuario_actualizado

def actualizar_contexto_temporal(wa_id: str, contexto: dict, db):
    """
    Actualiza el contexto temporal del usuario (para guardar datos temporales durante flujos)
    """
    repo = UserRepository(db)
    return repo.actualizar_contexto_temporal(wa_id, contexto)