from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.db import supabase
from datetime import datetime
from uuid import UUID
from fastapi import Cookie
from typing import Annotated
from fastapi import Header
from fastapi import Form
from fastapi import FastAPI, File
from fastapi import FastAPI, UploadFile
import httpx
from fastapi import FastAPI, HTTPException
from routers import users,items,auth
from app.services.auth_service import create_user
from fastapi import Depends
from routers import model
app = FastAPI()
app.include_router(users.router,prefix="/users")
app.include_router(items.router,prefix="/items")
app.include_router(auth.router,prefix="/auth")
app.include_router(model.router,prefix="/model")

def sample_depend():
    return "kartheek"

# ----------------------------
# Pydantic Model
# ----------------------------
class NewItem(BaseModel):
    name: str
    rate: int
    description: str | None = None
class UserResponse(BaseModel):
    id : int
    filename : str

# ----------------------------
# Fake Database
# ----------------------------
fake_db = {
    1: {"name": "pen", "rate": 100, "description": "very costly"},
    2: {"name": "pencil", "rate": 50, "description": "no"}
}

@app.get("/")
def sya_hello(name = Depends(sample_depend)):
    return {"welcome" : name}
# ----------------------------
# Basic User Route
# ----------------------------
@app.get("/users")
def data():
    return {"user": "default"}


# ----------------------------
# Shop Items
# ----------------------------
shop_items = {
    1: {"name": "pen", "rate": 10},
    2: {"name": "pencil", "rate": 20},
    3: {"name": "eraser", "rate": 5}
}


# ----------------------------
# Get Item by ID
# ----------------------------
@app.get("/items/{items_id}")
def items_data(items_id: int):

    response = supabase.table("fastsignin").select("*").eq("id", items_id).execute()

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return {"item": response.data}


# ----------------------------
# Pagination Example
# ----------------------------
dataa = [1, 2, 3, 4, 5, 67, 8]

@app.get("/items")
def para(skip: int = 0, limit: int = 10):
    return dataa[skip: skip + limit]


# ----------------------------
# User Item Route
# ----------------------------
shop_items1 = {
    1: {"name": "pen", "rate": 10, "instock": True},
    2: {"name": "pencil", "rate": 20, "instock": False},
    3: {"name": "eraser", "rate": 5, "instock": True}
}


@app.get("/users/{user_id}/00/{items_id}")
def get_user_item(
    user_id: int,
    items_id: int,
    discount: int = 0
):

    item = shop_items1.get(items_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    final_rate = item["rate"] - discount

    return {
        "user_checking": user_id,
        "item_name": item["name"],
        "original_rate": item["rate"],
        "discount_applied": discount,
        "final_price": final_rate
    }


# ----------------------------
# Search Route
# ----------------------------
@app.get("/search-items")
def search_items(
    query: str,
    limit: int = 5
):

    return {
        "searching_for": query,
        "limit_results": limit
    }


# ----------------------------
# Create New Item
# ----------------------------
@app.post("/items")
def get_item_data(item_data: NewItem):

    new_id = max(fake_db.keys()) + 1

    fake_db[new_id] = item_data.model_dump()

    return {
        "message": "Item added successfully",
        "item_id": new_id,
        "data": fake_db[new_id]
    }


# ----------------------------
# Get All Items from Fake DB
# ----------------------------
@app.get("/all-items")
def get_all_items():
    return fake_db

@app.get("/query")
def query_para(q : str , p: str | None = None):
    return {"you searched for" : q , "AND " : p }
    
# @app.post("/time")
# def create_time(event_time : datetime):
#     return {event_time}
@app.get("/profile")
def uses_profile(session_id : Annotated[str | None, Cookie()] = None):
    return {"your session id is": session_id}

@app.get("/headers")
def headers(hid: str=Header()):
    return {hid}


@app.post("/signin")
async def signin(username : str=Form(),id: str = Form() , file : UploadFile=File()):
    contents=await file.read()
    data = {
        "username": username,
        "user_id": id,
        "filename": file.filename
    }
    response=create_user(data)
    return {"message": "Data inserted successfully","response": response}
content=""
@app.get("/get-users",response_model=UserResponse)
async def get_user():
    response = supabase.table("fastsignin").select("*").execute()
    return response.data[0] #this is used response model create above
@app.post("/upload")
async def upload(
    file: UploadFile
):
    contents = await file.read()
    
    return {
        "filename", contents  
    }