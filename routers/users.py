import models
from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.hash import bcrypt
from typing import Optional
import uuid
import sys
from typing import Optional
import uuid
sys.path.append("..")


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {
            "description": "Not Found"
        }
    }
)


