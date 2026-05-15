"""
SmartShip AI — unified entry point.
Runs the production FastAPI backend (not the legacy minimal API).
"""

import os
import sys

if __name__ == "__main__":
    import uvicorn

    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
    )
