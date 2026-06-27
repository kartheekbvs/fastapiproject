from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel
from app.db import supabase

router = APIRouter()
@router.get("/users")
def router_main():
    return {"message": "Welcome to the users router!"}

@router.get("/get-users")
def get_user():
    response = supabase.table("fastsignin").select("*").execute()
    return {"message": "Data retrieved successfully", "data": response.data}