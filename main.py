from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler # type: ignore
from slowapi.util import get_remote_address # type: ignore
from slowapi.errors import RateLimitExceeded # type: ignore
import logging
from dotenv import load_dotenv
from app.core.exceptions import handle_exceptions
from app.routes import analyze_routes, auth_routes
from app.middleware.custom_middleware import add_process_time_header

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Trade Opportunities API",
    description="AI-powered market analysis for trade opportunities in Indian sectors",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(add_process_time_header)

app.include_router(auth_routes.router)
app.include_router(analyze_routes.router)

@app.get("/")
async def root():
    "Root endpoint with API information"
    return {
        "message": "Trade Opportunities API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

# Add global exception handler
app.add_exception_handler(Exception, handle_exceptions)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)