from fastapi import APIRouter
from typing import Any, Optional, Dict, List

class BaseController:
    """
    Base controller class for NASA API controllers.
    
    This class provides common functionality for all NASA API controllers.
    """
    
    def __init__(self, router_prefix: str, tags: List[str]):
        """
        Initialize the controller with a router prefix and tags.
        
        Args:
            router_prefix: The prefix for all routes in this controller
            tags: The OpenAPI tags for all routes in this controller
        """
        self.router = APIRouter(prefix=router_prefix, tags=tags)
        self._register_routes()
    
    def _register_routes(self) -> None:
        """
        Register all routes for this controller.
        
        This method should be overridden by subclasses.
        """
        pass