from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# Import route modules
from webapp.ontology.routes import router as ontology_router
from webapp.kg.routes import router as kg_router
from webapp.rag.routes import router as rag_router

app = FastAPI(
    title="HazardSafe-KG",
    description="Unified platform for safety-relevant technical document analysis",
    version="1.0.0"
)

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
app.include_router(ontology_router, prefix="/ontology", tags=["ontology"])
app.include_router(kg_router, prefix="/kg", tags=["knowledge-graph"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])

@app.get("/")
async def root(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "HazardSafe-KG"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
