import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from database import engine
import models
from routers import users, auth, transactions, accounts
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from templates import settings
import utils

app = FastAPI(
    docs_url=None,
    redoc_url=None
)
security = HTTPBasic()

models.Base.metadata.create_all(bind=engine)

# Configure the username and password for your docs and redoc endpoint when deployed
VALID_USERNAME = settings.USERNAME
VALID_PASSWORD = settings.API_PASSWORD

# Dependency for Authentication
def authenticate(credentials: HTTPBasicCredentials = Depends(security, use_cache=False)):
    isAuthenticated = utils.authenticate_username_and_password(credentials.username, credentials.password)
    if isAuthenticated:
        return credentials

# Custom Docs Route with Authentication
@app.get("/", include_in_schema=False)
async def get_documentation(credentials: HTTPBasicCredentials = Depends(authenticate, use_cache = False)):
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="API Docs")

# Custom Redoc Route with Authentication
@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(credentials: HTTPBasicCredentials = Depends(authenticate, use_cache = False)):
    return get_redoc_html(openapi_url=app.openapi_url, title="ReDoc")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(accounts.router)