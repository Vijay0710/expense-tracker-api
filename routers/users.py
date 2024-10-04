import sys
sys.path.append("../..")

import models
from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from responses import user_response
from routers.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {
            "description": "Not Found"
        }
    }
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/user", response_model = user_response.UserResponseModel)
async def get_my_data(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User)\
            .filter(models.User.email_id == current_user.get("username"))\
            .first()
    
    return user


