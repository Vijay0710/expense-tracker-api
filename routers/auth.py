import sys
sys.path.append("../..")
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from typing import Optional
import models
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from jose import ExpiredSignatureError, jwt, JWTError
from exceptions import auth
import uuid
import templates.settings as settings
from exceptions import network

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
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class AddressModel(BaseModel):
    address_1: str
    address_2: Optional[str] = None
    city: str
    state: str
    country: str
    postal_code: str

class UserModel(BaseModel):
    full_name: str
    email_id: str
    password: str
    phone_number: str
    address: Optional[AddressModel] = None

class ForgetPasswordRequest(BaseModel):
    email: str

class UserResponseModel(BaseModel):
    id: uuid.UUID
    full_name: str
    email_id: str
    phone_number: str


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
    try:
        user = db.query(models.User)\
                    .filter(models.User.email_id == username)\
                    .first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The username or password is incorrect")
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The username or password is incorrect")
        
        return user
    
    except OperationalError:
        raise network.network_exception()

def create_access_token(username: str, user_id: uuid, expires_delta: Optional[timedelta] = None):
    encode = {
        "username" : username,
        "uuid" : str(user_id)
    }

    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    encode.update({ "exp" : expires })

    return jwt.encode(encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Token endpoint to get encypted information of the user
@router.post("/token")
async def login_user_and_create_access_token(form_data: OAuth2PasswordRequestFormStrict = Depends(), db: Session = Depends(get_db)):
    try:
        user = verify_user(form_data.username, form_data.password, db=db)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The username or password is invalid")
        
        token  = create_access_token(
            username=form_data.username, 
            user_id=user.id, 
            expires_delta=timedelta(minutes=15)
        )

        return {
            "access_token" : token,
            "token_type" : "Bearer"
        }
    
    except OperationalError:
        raise network.network_exception()


def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("username")
        user_id = payload.get("uuid")
        if username is not None and user_id is not None:
            return {
                "username" : username,
                "user_id" : user_id
            }
        raise auth.current_user_exception()
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Oops your Authorization is Expired. Please try logging in again"
        )
    
    except OperationalError:
        raise network.network_exception()
    
    except JWTError:
        raise auth.current_user_exception()


# User can register with or without address data
@router.post("/register")
def register_user(user: UserModel, db: Session = Depends(get_db)):
    try:
        user_data = db.query(models.User)\
                        .filter(models.User.email_id == user.email_id)\
                        .first()
        if user_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        
        create_user_model = models.User()
        
        create_user_model.id = uuid.uuid4()
        create_user_model.email_id = user.email_id
        create_user_model.hashed_password = get_hashed_password(user.password)
        create_user_model.full_name = user.full_name
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
        try:
            db.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        
        return {
            "status" : status.HTTP_201_CREATED,
            "detail" : "User registered successfully"
        }
    
    except OperationalError:
        raise network.network_exception()