import os
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import Response
from app.routers import webhook_router
from app.database.db_conn import get_db
from app.models.database_models import Parqueadero, User, GestorParqueadero, Suscripcion
from app.repositories.user_repositories import ConductorRepository, UserRepository, GestorParqueaderoRepository
from app.repositories.parqueadero_repository import ParqueaderoRepository
from app.repositories.suscripcion_repository import SuscripcionRepository
from app.services.notification_service import NotificationService

app = FastAPI()

app.include_router(webhook_router.router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

# @app.get("/get-db")
# async def get_db_info(db = Depends(get_db)):
#     return db.list_collection_names()

@app.post("/crear-usuario", deprecated=True)
async def crear_usuario(usuario_crear: User, db = Depends(get_db)):
    """
    Crea un nuevo usuario conductor (Debería hacerse por WhatsApp)
    """
    user_repo = ConductorRepository(db)
    result = user_repo.create(usuario_crear)
    return result.model_dump(by_alias=True)

@app.post("/crear-gestor")
async def crear_gestor(gestor_crear: GestorParqueadero, db = Depends(get_db)):
    """
    Crea un nuevo gestor de parqueadero
    - _id: Es el número de WhatsApp del gestor (Antecedido por 57, por el código de país) Ej: 573001234567
    - name: Nombre del gestor
    - rol: Debe ser "gestor_parqueadero"
    - estado_registro: Debe ser "completo"
    - **Parametros opcionales:**
        - parqueadero_id: ID del parqueadero que gestiona (opcional al crear, se puede asociar después)
        - estado_chat: Se puede inicializar vacío o con valores por defecto
    """
    user_repo = GestorParqueaderoRepository(db)
    print(gestor_crear.model_dump(by_alias=True))
    result = user_repo.create(gestor_crear)
    return result.model_dump(by_alias=True)

@app.put("/asociar-parqueadero-gestor")
async def asociar_parqueadero_gestor(wa_id: str, parqueadero_id: str, db = Depends(get_db)):
    gestor_repo = GestorParqueaderoRepository(db)
    parqueadero_repo = ParqueaderoRepository(db)
    parqueadero = parqueadero_repo.find_by_id(parqueadero_id)
    if not parqueadero:
        raise HTTPException(status_code=404, detail="Parqueadero no encontrado")
    gestor = gestor_repo.find_by_id(wa_id)
    if not gestor:
        raise HTTPException(status_code=404, detail="Gestor no encontrado")
    gestor.parqueadero_id = parqueadero.id
    gestor_repo.update(gestor)
    return {"message": "Parqueadero asociado al gestor exitosamente"}

@app.get("/usuarios")
async def listar_usuarios(db = Depends(get_db)):
    user_repo = UserRepository(db)
    usuarios = user_repo.find_all()
    return [u.model_dump(by_alias=True) for u in usuarios]

@app.post("/crear-parqueadero")
async def crear_parqueadero(parqueadero_crear: Parqueadero, db = Depends(get_db)):
    """
    Crea un nuevo parqueadero
    - Parámetros opcionales:
        - _id: Se asigna automáticamente si no se proporciona
        - ultima_actualizacion: Se asigna automáticamente si no se proporciona
    """
    parqueadero_repo = ParqueaderoRepository(db)
    result = parqueadero_repo.create(parqueadero_crear.model_dump(by_alias=True))
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result.model_dump(by_alias=True)

@app.get("/gestor/{gestor_id}/parqueadero")
async def obtener_parqueadero_gestor(gestor_id: str, db = Depends(get_db)):
    gestor_repo = GestorParqueaderoRepository(db)
    parqueadero_repo = ParqueaderoRepository(db)
    
    parqueadero_id = gestor_repo.obtener_parqueadero_id(gestor_id)
    if not parqueadero_id:
        raise HTTPException(status_code=404, detail="Gestor no encontrado o sin parqueadero asociado")
    
    parqueadero = parqueadero_repo.find_by_id(parqueadero_id)
    if not parqueadero:
        raise HTTPException(status_code=404, detail="Parqueadero no encontrado")
    
    return parqueadero.model_dump(by_alias=True)

@app.get("/parqueaderos")
async def listar_parqueaderos(db = Depends(get_db)):
    parqueadero_repo = ParqueaderoRepository(db)
    parqueaderos = parqueadero_repo.find_all()
    return [p.model_dump(by_alias=True) for p in parqueaderos]

# ===== ENDPOINTS DE SUSCRIPCIONES Y NOTIFICACIONES =====

@app.post("/suscribir-conductor")
async def suscribir_conductor(conductor_id: str, parqueadero_id: str = None, db = Depends(get_db)):
    """
    Suscribe un conductor a notificaciones de parqueaderos
    - conductor_id: WhatsApp ID del conductor (ej: 573001234567)
    - parqueadero_id: ID del parqueadero específico (opcional, si no se envía se suscribe a todos)
    """
    notification_service = NotificationService(db)
    result = notification_service.suscribir_conductor(conductor_id, parqueadero_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}

@app.delete("/desuscribir-conductor")
async def desuscribir_conductor(conductor_id: str, parqueadero_id: str = None, db = Depends(get_db)):
    """
    Desuscribe un conductor de notificaciones
    - conductor_id: WhatsApp ID del conductor
    - parqueadero_id: ID del parqueadero específico (opcional, si no se envía se desuscribe de todos)
    """
    notification_service = NotificationService(db)
    result = notification_service.desuscribir_conductor(conductor_id, parqueadero_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}

@app.get("/conductor/{conductor_id}/suscripciones")
async def listar_suscripciones_conductor(conductor_id: str, db = Depends(get_db)):
    """
    Lista las suscripciones activas de un conductor
    """
    notification_service = NotificationService(db)
    suscripciones = notification_service.listar_suscripciones_conductor(conductor_id)
    return {"suscripciones": suscripciones}

@app.put("/parqueadero/{parqueadero_id}/actualizar-cupos")
async def actualizar_cupos_parqueadero(
    parqueadero_id: str, 
    cupos_libres: str, 
    tiene_cupos: bool, 
    db = Depends(get_db)
):
    """
    Actualiza los cupos de un parqueadero y envía notificaciones automáticamente
    - parqueadero_id: ID del parqueadero
    - cupos_libres: Número de cupos libres (como string)
    - tiene_cupos: Boolean indicando si hay cupos disponibles
    """
    parqueadero_repo = ParqueaderoRepository(db)
    notification_service = NotificationService(db)
    
    # Verificar que el parqueadero existe
    parqueadero = parqueadero_repo.find_by_id(parqueadero_id)
    if not parqueadero:
        raise HTTPException(status_code=404, detail="Parqueadero no encontrado")
    
    # Actualizar cupos y enviar notificaciones
    result = parqueadero_repo.actualizar_cupos_con_notificacion(
        parqueadero_id, 
        cupos_libres, 
        tiene_cupos, 
        notification_service
    )
    
    return {
        "message": "Cupos actualizados exitosamente",
        "parqueadero": result["parqueadero"],
        "notificaciones_enviadas": result["notificaciones_enviadas"]
    }