"""
Simple VAD Demo Backend - Refactored
Real-time Voice Activity Detection using Silero VAD
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.websocket import router as websocket_router
from api.health import router as health_router

# Configure logging - enable DEBUG for detailed VAD logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simple VAD Demo", 
    description="Real-time Voice Activity Detection using Silero VAD",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket_router)
app.include_router(health_router)


if __name__ == "__main__":
    logger.info("Starting Simple VAD Demo Backend...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
