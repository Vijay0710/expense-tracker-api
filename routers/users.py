import sys
sys.path.append("..")

from fastapi import APIRouter
from database import SessionLocal, engine
import models

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {
            "description": "Not Found"
        }
    }
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/")
def greet_user():
    return {
        "detail" : "Hello User"
    }