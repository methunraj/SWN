from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.routes import chat_router, models_router, prompts_router, files_router
from app.middleware import setup_cors, setup_rate_limit, setup_exception_handlers
from app.agents import ChatAgent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global chat agent
chat_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Swift Neethi Backend...")
    
    # Initialize chat agent
    global chat_agent
    from app.routes.chat import chat_agent as route_agent
    
    # Ensure the agent is initialized
    if route_agent:
        logger.info("Chat agent already initialized")
    else:
        logger.info("Initializing chat agent...")
        chat_agent = ChatAgent()
        await chat_agent.initialize()
        logger.info("Chat agent initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Swift Neethi Backend...")
    if chat_agent:
        await chat_agent.cleanup()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Setup middleware
setup_cors(app)
setup_rate_limit(app)
setup_exception_handlers(app)

# Include routers
app.include_router(chat_router)
app.include_router(models_router)
app.include_router(prompts_router)
app.include_router(files_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )