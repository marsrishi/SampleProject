from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DBNAME = os.getenv("MONGODB_DB", "testdb")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

try:
    info = client.server_info()
    print("Connected! MongoDB version:", info.get("version"))
    db = client[DBNAME]
    result = db.test_collection.insert_one({"hello": "codespaces"})
    print("Inserted id:", result.inserted_id)
    doc = db.test_collection.find_one({"_id": result.inserted_id})
    print("Read back:", doc)
    db.test_collection.delete_one({"_id": result.inserted_id})
    print("Test document inserted and removed successfully.")
except Exception as e:
    print("Connection failed:", e)
finally:
    client.close()