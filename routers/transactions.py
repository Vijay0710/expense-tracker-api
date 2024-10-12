import sys
sys.path.append("../..")

import models
from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from responses import user_response
from routers.auth import get_current_user


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={
        404: {
            "description": "No Transactions Found"
        }
    }
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()