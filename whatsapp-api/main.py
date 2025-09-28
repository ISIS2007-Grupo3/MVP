from fastapi import FastAPI
from database.db_conn import get_db
app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/get-db")
async def get_db_info():
    db = get_db()
    return {"databases": db.list_collection_names()}