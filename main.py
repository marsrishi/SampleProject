from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

# ----------------------------
# MongoDB connection
# ----------------------------
mongodb_client = MongoClient(MONGODB_URI)
db = mongodb_client[MONGODB_DB]

# ----------------------------
# FastAPI instance
# ----------------------------
app = FastAPI()

# ----------------------------
# Templates folder
# ----------------------------
templates = Jinja2Templates(directory="templates")

# ----------------------------
# Pydantic model for user
# ----------------------------
class User(BaseModel):
    name: str
    email: EmailStr
    bio: str = None

# ----------------------------
# API Endpoints (CRUD)
# ----------------------------

# Create user
@app.post("/users")
async def create_user(user: User):
    result = db["users"].insert_one(user.dict())
    new_user = db["users"].find_one({"_id": result.inserted_id})
    new_user["_id"] = str(new_user["_id"])
    return new_user

# Get all users
@app.get("/users")
async def get_users(request: Request):
    users_cursor = db["users"].find()
    users = []
    for u in users_cursor:
        u["_id"] = str(u["_id"])
        users.append(u)
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

# Get single user
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return user

# Update user
@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    result = db["users"].update_one(
        {"_id": ObjectId(user_id)}, {"$set": user.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = db["users"].find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    return updated_user

# Delete user
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = db["users"].delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}

# ----------------------------
# UI Routes
# ----------------------------

# Index page with list of users
@app.get("/ui/users")
async def ui_users(request: Request):
    users_cursor = db["users"].find()
    users = []
    for u in users_cursor:
        u["_id"] = str(u["_id"])
        users.append(u)
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

# Create User form
@app.get("/ui/users/new")
async def ui_create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/ui/users/new")
async def ui_create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    bio: str = Form(None)
):
    user = {"name": name, "email": email, "bio": bio}
    db["users"].insert_one(user)
    return RedirectResponse(url="/ui/users", status_code=303)

# Edit User form
@app.get("/ui/users/{user_id}/edit")
async def ui_edit_user_form(request: Request, user_id: str):
    user = db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@app.post("/ui/users/{user_id}/edit")
async def ui_edit_user(
    request: Request,
    user_id: str,
    name: str = Form(...),
    email: str = Form(...),
    bio: str = Form(None)
):
    db["users"].update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"name": name, "email": email, "bio": bio}}
    )
    return RedirectResponse(url="/ui/users", status_code=303)

# Delete User confirmation
@app.get("/ui/users/{user_id}/delete")
async def ui_delete_user(request: Request, user_id: str):
    user = db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db["users"].delete_one({"_id": ObjectId(user_id)})
    return RedirectResponse(url="/ui/users", status_code=303)
