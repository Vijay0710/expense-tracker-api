import sys
sys.path.append("../..")

import models
from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from responses.ResponseModels import UserResponseModel
from routers.auth import decode_jwt_and_get_current_user
from exceptions import network
from sqlalchemy.exc import OperationalError

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

@router.get("/user", response_model = UserResponseModel)
async def get_my_data(current_user: dict = Depends(decode_jwt_and_get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(models.User)\
                .filter(models.User.email_id == current_user.get("username"))\
                .first()
        
        return user

    except OperationalError:
        raise network.network_exception()
    


