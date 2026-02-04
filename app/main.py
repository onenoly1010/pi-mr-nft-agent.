"""
FastAPI application for Pi MR-NFT agent dashboard (optional).

Provides REST endpoints for:
- Model royalty tracking
- Catalyst pool status
- Maintainer reputation
- Handoff status
"""

import os
import sys
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from web3 import Web3

load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pi MR-NFT Agent",
    description="Sovereign inference royalty agent",
    version="1.0.0"
)


def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format."""
    if not address or address == "0x..." or address == "0xYourPiMainnetAddressHere...":
        return False
    try:
        return Web3.is_address(address) and address.startswith("0x") and len(address) == 42
    except Exception:
        return False


def validate_environment():
    """Validate required environment variables on startup."""
    required_vars = {
        "PI_NODE_RPC": "Pi Network RPC endpoint",
        "CREATOR_ADDRESS": "Creator/maintainer wallet address"
    }
    
    missing_vars = []
    invalid_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == "0x...":
            missing_vars.append(f"{var} ({description})")
        elif var == "CREATOR_ADDRESS" and not validate_ethereum_address(value):
            invalid_vars.append(f"{var} must be a valid Ethereum address (0x + 40 hex chars)")
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please copy .env.example to .env and configure your values")
        return False
    
    if invalid_vars:
        logger.error(f"Invalid environment variables: {', '.join(invalid_vars)}")
        return False
    
    # Log successful validation (without exposing sensitive data)
    logger.info("✓ Environment validation passed")
    logger.info(f"✓ RPC endpoint configured: {os.getenv('PI_NODE_RPC')[:30]}...")
    creator = os.getenv('CREATOR_ADDRESS')
    logger.info(f"✓ Creator address configured: {creator[:6]}...{creator[-4:]}")
    
    return True


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    logger.info("Starting Pi MR-NFT Agent...")
    
    if not validate_environment():
        logger.error("⚠️  WARNING: Running with incomplete configuration!")
        logger.error("⚠️  The application may not function correctly.")
        logger.error("⚠️  Please configure .env file with valid values.")
        # In production, you might want to sys.exit(1) here
        # For now, we'll allow it to run for demo purposes
    else:
        logger.info("✅ Pi MR-NFT Agent started successfully")
        logger.info("🚀 FastAPI server ready for requests")


@app.get("/health")
async def health_check():
    """
    Health check endpoint with environment validation.
    
    Returns:
        - status: "ok" if all checks pass
        - status: "degraded" if running with incomplete config
        - service metadata
    """
    env_valid = validate_environment()
    
    response = {
        "status": "ok" if env_valid else "degraded",
        "service": "pi-mr-nft-agent",
        "version": "1.0.0",
        "environment": {
            "rpc_configured": bool(os.getenv("PI_NODE_RPC")),
            "creator_configured": validate_ethereum_address(os.getenv("CREATOR_ADDRESS", "")),
            "catalyst_pool_configured": bool(os.getenv("CATALYST_POOL_ADDRESS")),
            "mr_nft_configured": bool(os.getenv("MR_NFT_ADDRESS"))
        }
    }
    
    if not env_valid:
        response["warnings"] = [
            "Running with incomplete configuration. Please configure .env file."
        ]
    
    return response


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
