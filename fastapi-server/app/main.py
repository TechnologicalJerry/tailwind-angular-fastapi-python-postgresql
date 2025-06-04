from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from app.routes import auth
from app.database import engine
from app.models import Base
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from fastapi_jwt_auth import AuthJWT
from app.config import settings

app = FastAPI()
app.include_router(auth.router)

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(SlowAPIMiddleware)

# Jinja2 for rendering HTML templates
templates = Jinja2Templates(directory="templates")

# Create DB tables
Base.metadata.create_all(bind=engine)

# JWT Config
class AuthSettings:
    authjwt_secret_key: str = settings.jwt_secret_key

@AuthJWT.load_config
def get_config():
    return AuthSettings()

# Optional: HTML page route
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
