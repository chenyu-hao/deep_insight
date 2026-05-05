import sys
import asyncio
import warnings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import logger
from app.api.endpoints import router
from app.services.hotnews.hot_news_scheduler import hot_news_scheduler

# Filter Pydantic warnings
warnings.filterwarnings("ignore", message="Field name.*shadows an attribute in parent.*", category=UserWarning)

def initialize_system():
    """System initialization logic"""
    # Force ProactorEventLoop on Windows for Playwright compatibility
    if sys.platform == 'win32':
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            logger.info("✅ WindowsProactorEventLoopPolicy applied successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to set WindowsProactorEventLoopPolicy: {e}")
    
    logger.info("🚀 System initialized.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚀 Starting hot news scheduler...")
    hot_news_scheduler.start()
    
    yield
    
    logger.info("🛑 Stopping hot news scheduler...")
    hot_news_scheduler.stop()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    initialize_system()
    
    app = FastAPI(
        title="News Opinion Analysis System",
        lifespan=lifespan
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🔒 Current Event Loop Policy: {asyncio.get_event_loop_policy()}")
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
