"""
Astronomy API controllers package.
"""

from api.controllers.astronomy_api.router import create_router
from api.controllers.astronomy_api.base_controller import BaseController
from api.controllers.astronomy_api.bodies_controller import BodiesController
from api.controllers.astronomy_api.events_controller import EventsController
from api.controllers.astronomy_api.search_controller import SearchController
from api.controllers.astronomy_api.admin_controller import AdminController

# Export all controllers
__all__ = [
    'create_router',
    'BaseController',
    'BodiesController',
    'EventsController',
    'SearchController',
    'AdminController',
]