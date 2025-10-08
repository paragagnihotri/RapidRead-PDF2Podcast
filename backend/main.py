from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router
from backend.config import settings

# Create FastAPI application
app = FastAPI(
    title="PDF to Podcast API",
    description="Convert PDF documents into engaging podcast scripts using AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api", tags=["podcast"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )