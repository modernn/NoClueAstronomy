from fastapi import APIRouter

from api.controllers.nasa_api.bodies_controller import BodiesController
from api.controllers.nasa_api.events_controller import EventsController
from api.controllers.nasa_api.search_controller import SearchController
from api.controllers.nasa_api.admin_controller import AdminController

def create_router() -> APIRouter:
    """
    Create and return the NASA API router with all controllers registered.
    
    Returns:
        FastAPI router with all NASA API controllers registered
    """
    # Create the main router
    router = APIRouter()
    
    # Initialize controllers
    bodies_controller = BodiesController()
    events_controller = EventsController()
    search_controller = SearchController()
    admin_controller = AdminController()
    
    # Include controllers' routers
    router.include_router(bodies_controller.router)
    router.include_router(events_controller.router)
    router.include_router(search_controller.router)
    router.include_router(admin_controller.router)
    
    return router