"""
CheckMate Virtue - Main Application Entry Point
FastAPI application with clean modular structure.
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, Any

from app.api import inspection_routes, vehicle_routes, invoice_routes
from app.config import settings
from app.utils.file_utils import load_json_file

# Available Industries
AVAILABLE_INDUSTRIES = {
    "automotive": {
        "name": "Automotive",
        "icon": "fas fa-car",
        "description": "Vehicle inspections and maintenance",
        "template_file": "app/templates/industries/automotive.json",
    },
    "construction": {
        "name": "Construction",
        "icon": "fas fa-hard-hat",
        "description": "Site safety and structural integrity",
        "template_file": "app/templates/industries/construction.json",
    },
    "food_safety": {
        "name": "Food Safety",
        "icon": "fas fa-utensils",
        "description": "Restaurant and kitchen hygiene",
        "template_file": "app/templates/industries/food_safety.json",
    },
    "healthcare": {
        "name": "Healthcare",
        "icon": "fas fa-hospital",
        "description": "Medical equipment and facility safety",
        "template_file": "app/templates/industries/healthcare.json",
    },
    "manufacturing": {
        "name": "Manufacturing",
        "icon": "fas fa-industry",
        "description": "Equipment and quality control",
        "template_file": "app/templates/industries/manufacturing.json",
    },
    "real_estate": {
        "name": "Real Estate",
        "icon": "fas fa-building",
        "description": "Property condition and maintenance",
        "template_file": "app/templates/industries/real_estate.json",
    },
    "it_datacenter": {
        "name": "IT & Data Centers",
        "icon": "fas fa-server",
        "description": "Infrastructure and security",
        "template_file": "app/templates/industries/it_datacenter.json",
    },
    "environmental": {
        "name": "Environmental",
        "icon": "fas fa-leaf",
        "description": "Compliance and waste management",
        "template_file": "app/templates/industries/environmental.json",
    },
}

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs" if settings.ENABLE_API_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Create templates instance
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(inspection_routes.router, prefix="/api/v1")
app.include_router(vehicle_routes.router, prefix="/api/v1")
app.include_router(invoice_routes.router, prefix="/api/v1")

# Root and web routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/industries", response_class=HTMLResponse)
async def list_industries(request: Request) -> HTMLResponse:
    """List industries page."""
    return templates.TemplateResponse(
        "industries.html", 
        {"request": request, "industries": AVAILABLE_INDUSTRIES}
    )


@app.get("/industries/{industry_id}/new", response_class=HTMLResponse)
async def new_industry_inspection(request: Request, industry_id: str) -> HTMLResponse:
    """New inspection form for specific industry."""
    if industry_id not in AVAILABLE_INDUSTRIES:
        raise HTTPException(status_code=404, detail="Industry not found")

    return templates.TemplateResponse(
        "new_industry_inspection.html",
        {
            "request": request,
            "industry_id": industry_id,
            "industry": AVAILABLE_INDUSTRIES[industry_id],
        },
    )


@app.get("/api/industries/{industry_id}/template")
async def get_industry_template_api(industry_id: str) -> Dict[str, Any]:
    """Get inspection template for specific industry."""
    template_file = settings.TEMPLATES_DIR / "industries" / f"{industry_id}.json"
    template = load_json_file(template_file)
    if template is None:
        raise HTTPException(status_code=404, detail="Industry template not found")
    return template


@app.get("/api/inspection-template")
async def get_inspection_template() -> Dict[str, Any]:
    """Get the basic inspection template (for backward compatibility)."""
    template_file = settings.BASE_DIR / "basic_inspection.json"
    template = load_json_file(template_file)
    if template is None:
        raise HTTPException(status_code=404, detail="Inspection template not found")
    return template


@app.get("/inspections", response_class=HTMLResponse)
async def list_inspections_page(request: Request) -> HTMLResponse:
    """List inspections page."""
    return templates.TemplateResponse("inspections.html", {"request": request})


@app.get("/inspections/new", response_class=HTMLResponse)
async def new_inspection_page(request: Request) -> HTMLResponse:
    """New inspection page."""
    return templates.TemplateResponse("new_inspection.html", {"request": request})


@app.get("/inspection/", response_class=HTMLResponse)
async def inspection_root_page(request: Request) -> HTMLResponse:
    """Inspection root page - redirect to form."""
    return templates.TemplateResponse("redirect_to_guided_inspection.html", {"request": request})


@app.get("/inspection/form", response_class=HTMLResponse)
async def inspection_form_page(request: Request) -> HTMLResponse:
    """Inspection form page."""
    try:
        # Load the basic inspection template
        template_file = settings.BASE_DIR / "basic_inspection.json"
        template = load_json_file(template_file, {})
        
        return templates.TemplateResponse(
            "inspection_form.html", 
            {
                "request": request,
                "template": template
            }
        )
    except Exception as e:
        print(f"Error rendering template: {e}")
        raise HTTPException(status_code=500, detail=f"Template error: {str(e)}")


@app.get("/inspection/list", response_class=HTMLResponse)
async def inspection_list_page(request: Request) -> HTMLResponse:
    """Inspection list page."""
    return templates.TemplateResponse("inspection_list.html", {"request": request})


@app.get("/inspection/{inspection_id}", response_class=HTMLResponse)
async def view_inspection_page(request: Request, inspection_id: str) -> HTMLResponse:
    """View inspection page."""
    return templates.TemplateResponse("view_inspection.html", {"request": request, "inspection_id": inspection_id})


@app.get("/test-vin", response_class=HTMLResponse)
async def test_vin_page(request: Request) -> HTMLResponse:
    """VIN test page."""
    return templates.TemplateResponse("test_vin_frontend.html", {"request": request})


@app.get("/test-vin-simple", response_class=HTMLResponse)
async def test_vin_simple_page(request: Request) -> HTMLResponse:
    """Simple VIN test page."""
    return templates.TemplateResponse("test_vin_simple.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.IS_PRODUCTION,
    ) 