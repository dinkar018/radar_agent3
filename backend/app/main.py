import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.utils.helpers import ensure_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup create data dirs (kb, papers, radar_data, results), init DB, log startup
    logger.info("Initializing directories...")
    ensure_dir(settings.UPLOAD_DIR)
    ensure_dir(settings.KB_DIR)
    ensure_dir(settings.PAPERS_DIR)
    ensure_dir(settings.RADAR_DATA_DIR)
    ensure_dir(settings.RESULTS_DIR)
    
    logger.info("Initializing database...")
    await init_db()
    
    logger.info("Startup complete.")
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan, title="Radar Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import knowledge_base, experiments, data, agent
from app.api import websocket

app.include_router(knowledge_base.router, prefix="/api")
app.include_router(experiments.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(websocket.router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Ensure directories exist before mounting static files
ensure_dir(settings.UPLOAD_DIR)
ensure_dir(settings.KB_DIR)
ensure_dir(settings.PAPERS_DIR)
ensure_dir(settings.RADAR_DATA_DIR)
ensure_dir(settings.RESULTS_DIR)

app.mount("/api/results", StaticFiles(directory=settings.RESULTS_DIR), name="results")

