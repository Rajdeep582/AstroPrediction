"""Start the API from the backend folder:  .venv/Scripts/python run.py"""
import sys
from pathlib import Path

import uvicorn

from app.config import API_HOST, API_PORT

if __name__ == "__main__":
    prod = "--prod" in sys.argv
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=not prod,
        reload_dirs=None if prod else [str(Path(__file__).parent / "app")],
        workers=1,
        log_level="warning" if prod else "info",
    )
