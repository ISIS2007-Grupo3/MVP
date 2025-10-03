from app.repositories.base_repository import BaseRepository
from app.models.whatsapp_webhook import Message
class MessageRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, "mensajes", Message)

    def crear_mensaje(self, mensaje: dict):
        self.collection.insert_one(mensaje)

    def obtener_mensajes(self, usuario_id):
        return self.collection.find({"to": usuario_id})

    def eliminar_mensaje(self, mensaje_id):
        self.collection.delete_one({"_id": mensaje_id})