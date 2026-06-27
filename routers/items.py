from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel
from app.db import supabase
router=APIRouter()
@router.get("/")
def item_main():
    return {"message": "Welcome to the items router!"}
@router.get("/hello")
def hello():
    return {"message": "Hello, World!"}