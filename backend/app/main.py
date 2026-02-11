"""
FastAPI Main Application
Historical RAG Backend - Echoes of History
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import torch
from transformers import AutoTokenizer, AutoModel

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

from app.config import get_settings
from app.services.rag_service import RAGSystem
from app.services.llm_service import LLMService, HistoricalRAGPipeline
from app.routers import chat, tts, stt

# Global state
app_state = {
    "rag_system": None,
    "llm_service": None,
    "rag_pipeline": None,
    "hist_tokenizer": None,
    "hist_model": None,
    "device": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("=" * 60)
    logger.info("🏛️  HISTORICAL RAG SYSTEM STARTUP")
    logger.info("=" * 60)

    config = get_settings()

    # Determine device
    device = torch.device("cuda" if config.use_gpu and torch.cuda.is_available() else "cpu")
    app_state["device"] = device
    logger.info(f"Device: {device}")

    if device.type == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # Load Historical BERT
    try:
        logger.info(f"Loading Historical BERT: {config.historical_bert_model}")
        hist_tokenizer = AutoTokenizer.from_pretrained(config.historical_bert_model)
        hist_model = AutoModel.from_pretrained(config.historical_bert_model)
        hist_model.eval()
        hist_model = hist_model.to(device)

        app_state["hist_tokenizer"] = hist_tokenizer
        app_state["hist_model"] = hist_model
        logger.info("✅ Historical BERT loaded")

    except Exception as e:
        logger.error(f"Failed to load Historical BERT: {e}")
        logger.info("Falling back to roberta-base")
        hist_tokenizer = AutoTokenizer.from_pretrained("roberta-base")
        hist_model = AutoModel.from_pretrained("roberta-base")
        hist_model.eval()
        hist_model = hist_model.to(device)

        app_state["hist_tokenizer"] = hist_tokenizer
        app_state["hist_model"] = hist_model

    # Initialize RAG System
    try:
        logger.info("Initializing RAG System...")
        rag_system = RAGSystem(config)
        rag_system.initialize(
            hist_tokenizer,
            hist_model,
            device=str(device)
        )
        app_state["rag_system"] = rag_system
        logger.info("✅ RAG System initialized")

    except Exception as e:
        logger.error(f"Failed to initialize RAG System: {e}")
        raise

    # Initialize LLM Service
    try:
        logger.info("Initializing LLM Service...")
        llm_service = LLMService(config)
        llm_service.initialize()
        app_state["llm_service"] = llm_service
        logger.info("✅ LLM Service initialized")

    except Exception as e:
        logger.error(f"Failed to initialize LLM Service: {e}")
        raise

    # Create RAG Pipeline
    rag_pipeline = HistoricalRAGPipeline(
        retriever=rag_system.get_retriever(),
        llm_service=llm_service,
        config=config
    )
    app_state["rag_pipeline"] = rag_pipeline

    logger.info("=" * 60)
    logger.info("✅ SYSTEM READY")
    logger.info(f"📊 Documents indexed: {rag_system.get_document_count()}")
    logger.info(f"🎭 Characters available: 9")
    logger.info(f"🌐 Server running at http://{config.api_host}:{config.api_port}")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Historical RAG API",
    description="Echoes of History - Chat with historical figures using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to force 200 on all OPTIONS preflight with proper CORS headers
@app.middleware("http")
async def cors_preflight_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        origin = request.headers.get("origin", "*")
        req_headers = request.headers.get("access-control-request-headers", "*")
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = req_headers
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return await call_next(request)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    rag_system = app_state.get("rag_system")
    llm_service = app_state.get("llm_service")

    return {
        "status": "healthy",
        "version": "1.0.0",
        "models_loaded": {
            "historical_bert": app_state.get("hist_model") is not None,
            "rag_system": rag_system is not None and rag_system.is_initialized,
            "llm_service": llm_service is not None and llm_service.is_initialized,
        },
        "documents_indexed": rag_system.get_document_count() if rag_system else 0,
        "device": str(app_state.get("device", "unknown"))
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Historical RAG API - Echoes of History",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Generic CORS preflight handler
@app.options("/api/{path:path}")
async def preflight_handler(path: str):
    return Response(status_code=200)


# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(tts.router, prefix="/api", tags=["tts"])
app.include_router(stt.router, prefix="/api", tags=["stt"])


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )


# Make app_state accessible to routers
def get_app_state():
    """Get global app state."""
    return app_state


if __name__ == "__main__":
    import uvicorn
    config = get_settings()
    uvicorn.run(
        "app.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug
    )
