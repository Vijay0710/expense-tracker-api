import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from database import engine
import models
from routers import users, auth, transactions, accounts
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from templates import settings

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
    correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, VALID_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

# Custom Docs Route with Authentication
@app.get("/expense-tracker-docs", include_in_schema=False)
async def get_documentation(credentials: HTTPBasicCredentials = Depends(authenticate, use_cache = False)):
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="API Docs")

# Custom Redoc Route with Authentication
@app.get("/expense-tracker-redoc", include_in_schema=False)
async def get_redoc_documentation(credentials: HTTPBasicCredentials = Depends(authenticate, use_cache = False)):
    return get_redoc_html(openapi_url=app.openapi_url, title="ReDoc")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(accounts.router)