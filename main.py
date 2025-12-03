from pydantic import BaseModel, EmailStr
from bson import ObjectId

from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Pydantic model for user profile
class User(BaseModel):
    name: str
    email: EmailStr
    age: int


# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DBNAME = os.getenv("MONGODB_DB", "mydatabase")

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[DBNAME]

app = FastAPI(title="User Profile API")

@app.get("/")
def root():
    return {"message": "FastAPI + MongoDB is working!"}

# Create a simple endpoint to add a user profile
@app.post("/users/")
def create_user(user: User):
    # Convert Pydantic model to dictionary
    user_dict = user.dict()
    result = db.users.insert_one(user_dict)
    return {"inserted_id": str(result.inserted_id)}


# Endpoint to get all users
from bson import ObjectId  # add this import at the top

@app.get("/users/")
def get_users():
    users = []
    for user in db.users.find():
        user["_id"] = str(user["_id"])  # convert ObjectId to string
        users.append(user)
    return {"users": users}

from fastapi import HTTPException

@app.put("/users/{user_id}")
def update_user(user_id: str, user: User):
    result = db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"updated_id": user_id}

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    result = db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted_id": user_id}

