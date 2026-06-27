from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel
from app.db import supabase
router=APIRouter()
@router.get("/")
def auth_main():
    return {"message": "Welcome to the auth router!"}