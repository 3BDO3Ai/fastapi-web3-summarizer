from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from .routers import summary
from .database import engine, Base
from . import models

# Load environment variables
load_dotenv()

# API configuration from environment variables
API_TITLE = os.getenv("API_TITLE", "Web3 Article Summarizer API")
API_DESCRIPTION = os.getenv("API_DESCRIPTION", "A FastAPI application for summarizing articles with Web3 authentication")
API_VERSION = os.getenv("API_VERSION", "0.1.0")

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers
app.include_router(summary.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Web3 Article Summarizer API",
        "documentation": "/docs",
        "version": API_VERSION
    }
