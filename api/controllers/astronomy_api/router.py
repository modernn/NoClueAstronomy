from fastapi import APIRouter

from api.controllers.astronomy_api.bodies_controller import BodiesController
from api.controllers.astronomy_api.events_controller import EventsController
from api.controllers.astronomy_api.search_controller import SearchController
from api.controllers.astronomy_api.admin_controller import AdminController

def create_router() -> APIRouter:
    """
    Create and return the main Astronomy API router with all controllers registered.
    
    Returns:
        FastAPI router with all Astronomy API controllers registered
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