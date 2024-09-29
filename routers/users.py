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

class AddressModel(BaseModel):
    address_1: str
    address_2: Optional[str] = None
    city: str
    state: str
    country: str
    postal_code: str


class UserModel(BaseModel):
    fullName: str
    email: str
    password: str
    phone_number: str
    address: AddressModel

models.Base.metadata.create_all(bind=engine)

def get_hashed_password(password: str):
    return bcrypt.hash(password)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.post("/register")
def register_user(user: UserModel, db: Session = Depends(get_db)):
    user_data = db.query(models.User)\
                    .filter(models.User.email_id == user.email)\
                    .first()
    if user_data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    
    create_user_model = models.User()
    create_address_model = models.Address()
    
    create_user_model.id = uuid.uuid4()
    create_user_model.email_id = user.email
    create_user_model.hashed_password = get_hashed_password(user.password)
    create_user_model.full_name = user.fullName
    create_user_model.phone_number = user.phone_number
    create_user_model.address_id = uuid.uuid4()

    create_address_model.id = create_user_model.address_id
    create_address_model.address_1 = user.address.address_1
    create_address_model.address_2 = user.address.address_2
    create_address_model.city = user.address.city
    create_address_model.state = user.address.state
    create_address_model.country = user.address.country
    create_address_model.postal_code = user.address.postal_code
    
    db.add(create_user_model)
    db.add(create_address_model)

    db.commit()
    
    return {
        "detail" : "User registered successfully"
    }
