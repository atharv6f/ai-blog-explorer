from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import asyncpg
import redis.asyncio as redis
from typing import Dict, Any

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for service monitoring
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ai-blog-backend",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {
            "api": "healthy",
            "database": "unknown",
            "redis": "unknown"
        }
    }

    # Check database connection
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Test connection
            conn = await asyncpg.connect(database_url)
            await conn.fetchval("SELECT 1")
            await conn.close()
            health_status["checks"]["database"] = "healthy"
        else:
            health_status["checks"]["database"] = "not_configured"
    except Exception as e:
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        print(f"Database health check failed: {e}")

    # Check Redis connection
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        if redis_url:
            # Test connection
            r = redis.from_url(redis_url)
            await r.ping()
            await r.close()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not_configured"
    except Exception as e:
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
        print(f"Redis health check failed: {e}")

    # Determine HTTP status code
    if health_status["status"] == "healthy":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/Railway deployments
    """
    try:
        # Perform basic checks
        health = await health_check()
        return {"ready": True, "timestamp": datetime.utcnow().isoformat()}
    except:
        raise HTTPException(status_code=503, detail={"ready": False})

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/Railway deployments
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ai-blog-backend"
    }