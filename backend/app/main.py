from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import asyncio
from typing import List
from datetime import datetime

# Import API routers
from app.api import health, websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up FastAPI service...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Database URL configured: {'DATABASE_URL' in os.environ}")
    print(f"Redis URL configured: {'REDIS_URL' in os.environ}")

    yield

    # Shutdown
    print("Shutting down FastAPI service...")

app = FastAPI(
    title="AI Blog Backend API",
    description="Backend API for AI-powered blog platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://frontend:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Blog Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(websocket.router, tags=["websocket"])

# Basic WebSocket endpoint for testing
@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")

# Test endpoint for database connectivity
@app.get("/test/services")
async def test_services():
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "healthy",
            "database": "not_implemented",
            "redis": "not_implemented"
        }
    }

    # Test database connection (placeholder)
    try:
        # In production, this would test actual database connection
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            results["services"]["database"] = "configured"
    except Exception as e:
        results["services"]["database"] = f"error: {str(e)}"

    # Test Redis connection (placeholder)
    try:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            results["services"]["redis"] = "configured"
    except Exception as e:
        results["services"]["redis"] = f"error: {str(e)}"

    return results