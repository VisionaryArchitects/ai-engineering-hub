"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers import sessions, websocket
from app.adapters.factory import AdapterFactory

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Multi-LLM Control Room API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.app_env
    }


@app.get("/api/providers")
async def list_providers():
    """List supported model providers"""
    return {
        "providers": AdapterFactory.get_supported_providers()
    }


@app.get("/api/info")
async def get_info():
    """Get system information"""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "supported_providers": AdapterFactory.get_supported_providers(),
        "routing_patterns": ["broadcast", "round_robin", "coordinator", "voting"],
        "features": {
            "multi_model_chat": True,
            "websocket_support": True,
            "cost_tracking": True,
            "export_formats": ["json", "markdown"],
            "max_models_per_session": 5
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print(f"🚀 {settings.app_name} starting up...")
    print(f"Environment: {settings.app_env}")
    print(f"Supported providers: {AdapterFactory.get_supported_providers()}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print(f"👋 {settings.app_name} shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
