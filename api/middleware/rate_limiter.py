import time
import logging
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Tuple, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger(__name__)

class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    
    Implements a sliding window algorithm to limit requests per client.
    """
    
    def __init__(
        self, 
        app,
        rate_limit: int = 60,      # requests per minute
        window_size: int = 60,     # sliding window size in seconds
        block_time: int = 300,     # block time in seconds if rate limit is exceeded
        exclude_paths: List[str] = None,  # paths to exclude from rate limiting
    ):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_size = window_size
        self.block_time = block_time
        self.requests: Dict[str, List[float]] = {}  # client_id -> list of timestamps
        self.blocked_clients: Dict[str, float] = {}  # client_id -> unblock time
        
        # Default paths to exclude
        self.exclude_paths = exclude_paths or [
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/health",
            "/"
        ]
        
        # Start cleanup task
        asyncio.create_task(self._cleanup())
    
    async def _cleanup(self):
        """Periodically clean up old requests and unblock clients"""
        while True:
            try:
                now = time.time()
                
                # Remove old request timestamps
                for client_id, timestamps in list(self.requests.items()):
                    self.requests[client_id] = [ts for ts in timestamps if now - ts < self.window_size]
                    if not self.requests[client_id]:
                        del self.requests[client_id]
                
                # Remove expired blocks
                for client_id, unblock_time in list(self.blocked_clients.items()):
                    if now > unblock_time:
                        del self.blocked_clients[client_id]
                
                await asyncio.sleep(10)  # Run cleanup every 10 seconds
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}", exc_info=True)
                await asyncio.sleep(30)  # Wait longer if there's an error
    
    def get_client_id(self, request: Request) -> str:
        """
        Get a unique identifier for the client.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            A unique identifier for the client
        """
        # Use X-Forwarded-For header if available (for clients behind proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Optionally incorporate API key or user ID if available
        api_key = request.headers.get("X-API-Key", "")
        
        # Combine the identifiers to create a client ID
        return f"{client_ip}:{api_key}"
    
    def is_rate_limited(self, client_id: str) -> Tuple[bool, dict]:
        """
        Check if a client is currently rate limited.
        
        Args:
            client_id: The client ID to check
            
        Returns:
            A tuple containing:
                - Whether the client is rate limited
                - Rate limit information
        """
        now = time.time()
        
        # Check if client is blocked
        if client_id in self.blocked_clients:
            unblock_time = self.blocked_clients[client_id]
            if now < unblock_time:
                remaining_seconds = int(unblock_time - now)
                return True, {
                    "detail": f"Too many requests. Please try again in {remaining_seconds} seconds.",
                    "retry_after": remaining_seconds
                }
            else:
                # Client has served their block time
                del self.blocked_clients[client_id]
        
        # Get timestamps of previous requests in the current window
        timestamps = self.requests.get(client_id, [])
        
        # Remove timestamps that are outside the current window
        current_window_start = now - self.window_size
        timestamps = [ts for ts in timestamps if ts > current_window_start]
        
        # Update timestamps for this client
        self.requests[client_id] = timestamps
        
        # Check if rate limit is exceeded
        if len(timestamps) >= self.rate_limit:
            # Block the client
            unblock_time = now + self.block_time
            self.blocked_clients[client_id] = unblock_time
            
            return True, {
                "detail": f"Rate limit exceeded. Too many requests in a {self.window_size} second period. "
                         f"Please try again in {self.block_time} seconds.",
                "retry_after": self.block_time
            }
        
        # Add current request timestamp
        self.requests[client_id].append(now)
        
        # Calculate remaining requests
        remaining = self.rate_limit - len(timestamps) - 1
        
        return False, {"X-RateLimit-Remaining": remaining, "X-RateLimit-Limit": self.rate_limit}
    
    async def dispatch(self, request: Request, call_next):
        """
        Process a request through the middleware.
        
        Args:
            request: The FastAPI request object
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        # Skip rate limiting for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Get client ID and check rate limit
        client_id = self.get_client_id(request)
        is_limited, rate_limit_info = self.is_rate_limited(client_id)
        
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": rate_limit_info["detail"]},
                headers={"Retry-After": str(rate_limit_info["retry_after"])}
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to the response
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["X-RateLimit-Remaining"])
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["X-RateLimit-Limit"])
        
        return response