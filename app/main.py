"""
FastAPI application for Pi MR-NFT agent dashboard (optional).

Provides REST endpoints for:
- Model royalty tracking
- Catalyst pool status
- Maintainer reputation
- Handoff status
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI(
    title="Pi MR-NFT Agent",
    description="Sovereign inference royalty agent",
    version="1.0.0"
)

# Configure Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - displays dashboard with Speed Insights."""
    # Get data from other endpoints
    catalyst = await catalyst_status()
    maintainer = await maintainer_status()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "service_name": "Pi MR-NFT Agent",
            "version": "1.0.0",
            "status": "operational",
            "catalyst": catalyst,
            "maintainer": maintainer,
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "pi-mr-nft-agent",
        "version": "1.0.0"
    }


@app.get("/catalyst/status")
async def catalyst_status():
    """Get current catalyst pool status."""
    # TODO: Fetch from on-chain
    return {
        "pool_capacity": 1_000_000,
        "inferences_processed": 0,
        "current_multiplier": 8.0,
        "remaining_capacity": 1_000_000,
    }


@app.get("/models")
async def list_models():
    """List all registered MR-NFT models."""
    return {
        "total_models": 0,
        "models": []
    }


@app.get("/maintainer/status")
async def maintainer_status():
    """Get current maintainer reputation and status."""
    return {
        "github_handle": os.getenv("MAINTAINER_GITHUB", "onenoly1010"),
        "reputation_score": 95.0,
        "inferences_processed": 0,
        "phase": "active_custodian"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
