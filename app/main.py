import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force ProactorEventLoop on Windows for Playwright compatibility
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        logger.info("✅ WindowsProactorEventLoopPolicy applied successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to set WindowsProactorEventLoopPolicy: {e}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(title="News Opinion Analysis System")

# CORS is crucial for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # Disable reload to prevent subprocesses from resetting the EventLoopPolicy on Windows
    # Pass the app instance directly
    logger.info(f"🔒 Current Event Loop Policy: {asyncio.get_event_loop_policy()}")
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
