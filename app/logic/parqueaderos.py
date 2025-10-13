
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.repositories.user_repositories import GestorParqueaderoRepository


def obtener_parqueaderos_con_cupos(db):
    parqueadero_repo = ParqueaderoRepository(db)
    return parqueadero_repo.find_with_available_spots()

def obtener_parqueadero_gestor(wa_id: str, db):
    gestor_repo = GestorParqueaderoRepository(db)
    return gestor_repo.obtener_parqueadero(wa_id)

def actualizar_cupos_parqueadero(wa_id: str, cupos_libres: str, tiene_cupo: bool, db):
    parqueadero = obtener_parqueadero_gestor(wa_id, db)
    print(parqueadero)
    if parqueadero:
        parqueadero_repo = ParqueaderoRepository(db)
        parqueadero_repo.actualizar_cupos(parqueadero, cupos_libres, tiene_cupo)
        return True
    return False