"""
DriftLens Deep Analyzer - FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.git_puller import git_puller
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DriftLens Deep Analyzer",
    description="Deep drift detection using Jaccard + Cosine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup():
    """Start background git puller on startup."""
    logger.info("🚀 DriftLens Deep Analyzer starting...")
    git_puller.start()
    logger.info("✅ Git puller started!")


@app.on_event("shutdown")
async def shutdown():
    """Stop git puller on shutdown."""
    git_puller.stop()
    logger.info("👋 DriftLens Deep Analyzer stopped!")
