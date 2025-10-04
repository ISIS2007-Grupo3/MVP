
from app.repositories.parqueadero_repository import ParqueaderoRepository


def obtener_parqueaderos_con_cupos(db):
    parqueadero_repo = ParqueaderoRepository(db)
    return parqueadero_repo.find_with_available_spots()