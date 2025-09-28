from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

def get_db():
    url = os.getenv("MONGO_URL")
    print(url)
    client = MongoClient(url)
    return client.get_database("test")