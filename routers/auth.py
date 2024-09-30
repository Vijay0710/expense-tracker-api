from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from typing import Optional
import models
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestFormStrict, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import uuid

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        404: {
            "description": "Not Authorized"
        }
    }
)

models.Base.metadata.create_all(bind=engine)

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
    address: Optional[AddressModel] = None


def get_hashed_password(password: str):
    return bcrypt.hash(password)

def verify_password(plain_password: str, hash_password: str):
    return bcrypt.verify(plain_password, hash_password)
    

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def verify_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User)\
                .filter(models.User.email_id == username)\
                .first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The username or password is incorrect")
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The username or password is incorrect")
    
    return user


#User can register with or without address data
@router.post("/register")
def register_user(user: UserModel, db: Session = Depends(get_db)):
    user_data = db.query(models.User)\
                    .filter(models.User.email_id == user.email)\
                    .first()
    if user_data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    
    create_user_model = models.User()
    
    create_user_model.id = uuid.uuid4()
    create_user_model.email_id = user.email
    create_user_model.hashed_password = get_hashed_password(user.password)
    create_user_model.full_name = user.fullName
    create_user_model.phone_number = user.phone_number

    if user.address != None:
        create_user_model.address_id = uuid.uuid4()
        create_address_model = models.Address()
        create_address_model.id = create_user_model.address_id
        create_address_model.address_1 = user.address.address_1
        create_address_model.address_2 = user.address.address_2
        create_address_model.city = user.address.city
        create_address_model.state = user.address.state
        create_address_model.country = user.address.country
        create_address_model.postal_code = user.address.postal_code
        db.add(create_address_model)
    
    db.add(create_user_model)
    db.commit()
    
    return {
        "detail" : "User registered successfully"
    }