import sys

import utils
sys.path.append("../..")
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request, status, APIRouter
from pydantic import BaseModel
from typing import Any, Optional
import models
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict, HTTPBasic
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import SecurityScheme
from fastapi.openapi.models import SecurityBase as SecurityBaseModel
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, jwt, JWTError
from exceptions import auth
import uuid
import templates.settings as settings
from exceptions import network
import base64

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        404: {
            "description": "Not Authorized"
        }
    }
)

class RefreshToken(BaseModel):
    refresh_token: str

class BasicAuth(SecurityBase):
    def __init__(self, scheme_name: str = None, auto_error: bool = True):
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

        self.model = SecurityBaseModel(
            type='http',
            description='Basic Authorization to validate API from Known sources'
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("X-Auth-Basic")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "basic":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Not authenticated"
                )
            else:
                return None
        return param

models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
basic_auth = BasicAuth(auto_error=False)

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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The username or password is incorrect")
        
        return user
    
    except OperationalError:
        raise network.network_exception()

def create_token(username: str, user_id: uuid, expires_delta: Optional[timedelta] = None, additional_claims: dict[str, Any] = {}):
    encode = {
        "username" : username,
        "uuid" : str(user_id)
    }

    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    encode.update({ "exp" : expires })
    encode.update(additional_claims)

    return jwt.encode(encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Token endpoint to get encypted information of the user
@router.post("/token")
async def login_user_and_create_access_token(form_data: OAuth2PasswordRequestFormStrict = Depends(), db: Session = Depends(get_db), basic_auth: BasicAuth = Depends(basic_auth)):
    if not basic_auth:
        raise HTTPException(
            headers={"WWW-X-Auth-Basic": "Basic"}, 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Kindly provide valid authentication method'
        )
    
    try:
        user = verify_user(form_data.username, form_data.password, db=db)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The username or password is invalid")
        
        token  = create_token(
            username=form_data.username, 
            user_id=user.id, 
            expires_delta=timedelta(minutes=15),
            additional_claims = {
                "token_type" : "Bearer"
            }
        )

        refresh_token = create_token(
            username=form_data.username,
            user_id=user.id,
            expires_delta=timedelta(days=7),
            additional_claims = {
                "token_type" : "Refresh"
            }
        )

        return {
            "access_token" : token,
            "refresh_token": refresh_token,
            "user_id": user.id
        }
    
    except OperationalError:
        raise network.network_exception()

@router.post("/refresh_token")
async def refresh_token(refresh_token: RefreshToken):
    try:
        payload = jwt.decode(refresh_token.refresh_token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("token_type") != "Refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        username = payload.get("username")
        user_id = payload.get("uuid")
        
        if not username or not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        
        access_token  = create_token(
            username=username, 
            user_id=user_id, 
            expires_delta=timedelta(minutes=15),
            additional_claims = {
                "token_type" : "Bearer"
            }
        )

        return {
            "access_token" : access_token,
            "user_id" : user_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong at server end.")
    
    except OperationalError:
        raise network.network_exception()


def get_current_user(basic_auth: BasicAuth = Depends(basic_auth),
                    token: str = Depends(oauth2_bearer)):
    if not basic_auth:
        raise HTTPException(
            headers={"WWW-X-Auth-Basic": "Basic"}, 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Kindly provide valid authentication method'
        )
    try:
        decoded = base64.b64decode(basic_auth).decode("ascii")
        api_username, _, api_password = decoded.partition(":")
        
        utils.authenticate_username_and_password(api_username, api_password)

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


@router.post("/verify_token")
def verify_token(refreshTokenModel: RefreshToken, basic_auth: BasicAuth = Depends(basic_auth)):
    if not basic_auth:
        raise HTTPException(
            headers={"WWW-X-Auth-Basic": "Basic"}, 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Kindly provide valid authentication method'
        )
    try:
        payload = jwt.decode(refreshTokenModel.refresh_token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

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
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Something went wrong when validating your credentials. Please try logging in again"
        )

# User can register with or without address data
@router.post("/register")
def register_user(user: UserModel, db: Session = Depends(get_db)):
    try:
        user_data = db.query(models.User)\
                        .filter(models.User.email_id == user.email_id)\
                        .first()
        if user_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        else:
            create_user_model = models.User(
                id = uuid.uuid4(),
                **user.model_dump(exclude={"address", "password"}),
                hashed_password = get_hashed_password(user.password)
            )

            db.add(create_user_model)

            if user.address:
                create_address_model = models.Address(
                    id=uuid.uuid4(),
                    **(user.address).__dict__,
                    user_id = create_user_model.id
                )
                db.add(create_address_model)
            
            db.commit()
                
        return {
            "status" : status.HTTP_201_CREATED,
            "detail" : "User registered successfully"
        }
        
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    
    except OperationalError:
        raise network.network_exception()