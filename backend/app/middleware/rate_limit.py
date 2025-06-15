from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 60, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = timedelta(seconds=period)
        self.clients = defaultdict(list)
        self.cleanup_task = None
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_id = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for certain paths
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)
        
        now = datetime.utcnow()
        
        # Clean old entries
        self.clients[client_id] = [
            timestamp for timestamp in self.clients[client_id]
            if now - timestamp < self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_id]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Record this request
        self.clients[client_id].append(now)
        
        # Process request
        response = await call_next(request)
        return response
    
    async def cleanup_old_entries(self):
        """Periodically clean up old entries to prevent memory leak"""
        while True:
            await asyncio.sleep(300)  # Clean every 5 minutes
            now = datetime.utcnow()
            
            for client_id in list(self.clients.keys()):
                self.clients[client_id] = [
                    timestamp for timestamp in self.clients[client_id]
                    if now - timestamp < self.period
                ]
                
                if not self.clients[client_id]:
                    del self.clients[client_id]


def setup_rate_limit(app):
    """Setup rate limiting middleware"""
    
    rate_limit = RateLimitMiddleware(
        app,
        calls=settings.rate_limit_per_minute,
        period=60
    )
    
    app.add_middleware(RateLimitMiddleware, calls=settings.rate_limit_per_minute)