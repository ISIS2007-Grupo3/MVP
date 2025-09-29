from pymongo.database import Database
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

class BaseRepository:
    def __init__(self, db: Database, collection_name: str, model: Type[BaseModel]):
        self.db = db
        self.collection = db[collection_name]
        self.model = model

    def find_all(self) -> List[BaseModel]:
        documents = self.collection.find()
        encontrados = []
        for doc in documents:
            encontrados.append(self.model(**doc))
        return encontrados
    
    def find_by_id(self, id: str) -> Optional[BaseModel]:
        document = self.collection.find_one({"_id": id})
        return self.model(**document) if document else None

    def create(self, data: Dict[str, Any]) -> BaseModel:
        validated_data = self.model(**data)
        self.collection.insert_one(validated_data.model_dump(by_alias=True))
        return validated_data

    def update(self, id: str, data: Dict[str, Any]) -> Optional[BaseModel]:
        self.collection.update_one({"_id": id}, {"$set": data})
        return self.find_by_id(id)

    def delete(self, id: str) -> bool:
        result = self.collection.delete_one({"_id": id})
        return result.deleted_count > 0