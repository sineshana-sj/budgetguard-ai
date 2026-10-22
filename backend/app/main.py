import app._path_cleaner
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.storage.database import init_db
from app.api.routes import router


app = FastAPI(
    title=settings.app_name,
    description="Intelligent Request Router powered by Strands Decider 2B & Amazon Bedrock",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Development & dashboard origin flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Mount API routes
app.include_router(router)
