"""
Main FastAPI application for HazardSafe-KG platform.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import logging
from pathlib import Path
import uvicorn
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

# Import routers
from webapp.ontology.routes import router as ontology_router
from webapp.kg.routes import router as kg_router
from webapp.nlp_rag.routes import router as nlp_rag_router
from webapp.validation.routes import router as validation_router
from webapp.quality.routes import router as quality_router

# Import backend modules
from ontology.manager import init_ontology_manager
from kg.database import init_database
from nlp_rag.processors.vector_store import init_vector_store
from validation.rules import validation_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logging.info("Starting HazardSafe-KG platform...")
    
    try:
        # Initialize ontology manager
        await init_ontology_manager()
        logging.info("Ontology manager initialized")
        
        # Initialize Neo4j database
        # For AuraDB, you'll need to set these environment variables:
        # NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io:7687
        # NEO4J_USER=neo4j
        # NEO4J_PASSWORD=HazardSafe123
        await init_database()
        logging.info("Neo4j database initialized")
        
        # Initialize vector store
        await init_vector_store()
        logging.info("Vector store initialized")
        
        # Validation engine is already initialized as a global instance
        logging.info("Validation engine initialized")
        
        logging.info("HazardSafe-KG platform started successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logging.info("Shutting down HazardSafe-KG platform...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="HazardSafe-KG",
    description="Unified platform for hazardous substance knowledge management",
    version="1.0.0",
    lifespan=lifespan
)

# Setup logging
def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "hazardsafe-kg.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ]
    )

# Setup logging
setup_logging()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="webapp/templates")

# Include routers
app.include_router(ontology_router, tags=["ontology"])
app.include_router(kg_router, tags=["knowledge-graph"])
app.include_router(nlp_rag_router, tags=["nlp_rag"])
app.include_router(validation_router, tags=["validation"])
app.include_router(quality_router, tags=["quality"])

@app.get("/")
async def root(request: Request):
    """Root endpoint serving the main dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "HazardSafe-KG",
        "version": "1.0.0"
    }

@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "HazardSafe-KG API",
        "version": "1.0.0",
        "description": "Unified platform for hazardous substance knowledge management",
        "endpoints": {
            "ontology": "/ontology",
            "knowledge_graph": "/kg",
            "nlp_rag": "/nlp_rag",
            "health": "/health"
        }
    }

@app.get("/api/stats")
async def get_platform_stats():
    """Get platform statistics."""
    try:
        from kg.database import neo4j_db
        from nlp_rag.processors.vector_store import vector_store
        from ontology.manager import ontology_manager
        from ingestion.haz_ingest import ingestion_pipeline
        
        # Get database stats
        db_stats = {}
        if neo4j_db.connected:
            db_stats = await neo4j_db.get_graph_stats()
        
        # Get vector store stats
        vs_stats = await vector_store.get_stats()
        
        # Get ontology stats
        ont_stats = await ontology_manager.get_ontology_stats()
        
        # Get ingestion stats
        ingestion_stats = await ingestion_pipeline.get_ingestion_stats()
        
        return {
            "database": db_stats,
            "vector_store": vs_stats,
            "ontology": ont_stats,
            "ingestion": ingestion_stats,
            "platform": {
                "app_name": os.getenv("APP_NAME", "HazardSafe-KG"),
                "version": os.getenv("APP_VERSION", "1.0.0"),
                "debug": os.getenv("DEBUG", "false").lower() == "true"
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting platform stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get platform statistics")

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return templates.TemplateResponse(
        "404.html", 
        {"request": request, "message": "Page not found"}, 
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors."""
    logging.error(f"Internal server error: {exc}")
    return templates.TemplateResponse(
        "500.html", 
        {"request": request, "message": "Internal server error"}, 
        status_code=500
    )

@app.get("/system-flowchart")
async def system_flowchart(request: Request):
    """Serve the system architecture flowchart"""
    return templates.TemplateResponse("architecture/index.html", {"request": request})

@app.get("/kg")
async def kg(request: Request):
    return templates.TemplateResponse("kg/index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
