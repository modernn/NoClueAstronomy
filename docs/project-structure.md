# NoClueAstronomy API Project Structure

## Directory Structure

```
noclue-astronomy-api/
│
├── api/                       # Main application package
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration settings
│   ├── main.py                # FastAPI application entry point
│   │
│   ├── controllers/           # API controllers (route handlers)
│   │   ├── __init__.py
│   │   ├── admin_controller.py
│   │   ├── base_controller.py
│   │   ├── bodies_controller.py
│   │   ├── events_controller.py
│   │   ├── router.py
│   │   └── search_controller.py
│   │
│   ├── middleware/            # Middleware components
│   │   ├── __init__.py
│   │   └── rate_limiter.py    # Rate limiting middleware
│   │
│   ├── models/                # Database models
│   │   ├── __init__.py
│   │   ├── cached_body.py
│   │   ├── cached_event.py
│   │   └── search_history.py
│   │
│   ├── schemas/               # Pydantic schemas for request/response validation
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── body.py
│   │   ├── event.py
│   │   └── search.py
│   │
│   └── services/              # Business logic and external API communication
│       ├── __init__.py
│       ├── api/                # External API clients
│       │   ├── __init__.py
│       │   ├── api_client.py
│       │   ├── astronomy_api_client.py
│       │   └── nasa_api_client.py
│       │
│       ├── api_gateway_service.py
│       ├── astronomy_provider.py
│       ├── astronomy_api.py
│       ├── body_service.py
│       ├── cache_service.py
│       ├── event_service.py
│       ├── health_service.py
│       └── search_service.py
│
├── data/                      # Directory for SQLite database
│   └── astronomy.db           # SQLite database file
│
├── scripts/                   # Utility scripts
│   ├── __init__.py
│   └── init_data.py           # Database initialization script
│
├── tests/                     # Test directory
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures and configuration
│   ├── test_api.py            # API test module
│   ├── test_services.py       # Service test module
│   └── test_controllers.py    # Controller test module
│
├── client/                    # Command-line client utility
│   ├── __init__.py
│   ├── client.py              # Main client script
│   └── commands/              # Client commands
│       ├── __init__.py
│       ├── body_commands.py
│       ├── event_commands.py
│       └── admin_commands.py
│
├── docs/                      # Additional documentation
│   ├── api_documentation.md
│   ├── integration_guide.md
│   └── deployment/
│       ├── aws_deployment.md
│       └── heroku_deployment.md
│
├── .dockerignore              # Docker ignore file
├── .env                       # Environment variables (created from .env.example)
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
├── start.bat                  # Windows startup script
├── start.sh                   # Linux/macOS startup script
├── README.md                  # Project documentation
└── PROJECT_STRUCTURE.md       # This file
```

## Key Components

### Application Structure

The application follows a layered architecture with the following components:

#### Controllers

Controllers handle HTTP requests and responses. They are responsible for:
- Parsing request parameters
- Validating input data
- Calling appropriate services
- Formatting responses

Each controller focuses on a specific resource or feature area:
- `bodies_controller.py`: Celestial body information
- `events_controller.py`: Astronomical events
- `search_controller.py`: Search functionality
- `admin_controller.py`: Administration endpoints

#### Services

Services contain the business logic of the application. They:
- Interact with the database
- Call external APIs through the API Gateway
- Handle caching logic
- Process data

Key services include:
- `body_service.py`: Manages celestial body data
- `event_service.py`: Handles astronomical event data
- `search_service.py`: Provides search functionality
- `cache_service.py`: Manages caching operations
- `health_service.py`: Monitors API health

#### API Clients

API clients handle communication with external APIs:
- `astronomy_api_client.py`: Client for the Astronomy API
- `nasa_api_client.py`: Client for the NASA API

The `api_gateway_service.py` acts as a facade for all external API clients, providing a unified interface for services.

#### Middleware

- `rate_limiter.py`: Implements rate limiting using a sliding window algorithm

#### Models

Database models using SQLAlchemy ORM:
- `cached_body.py`: Cached celestial body data
- `cached_event.py`: Cached astronomical event data
- `search_history.py`: Record of search queries

#### Schemas

Pydantic schemas for request and response validation:
- `body.py`: Schemas for celestial body data
- `event.py`: Schemas for astronomical event data
- `search.py`: Schemas for search functionality
- `admin.py`: Schemas for administration endpoints

### Database

The API uses SQLite with the following tables:
- **cached_bodies**: Stores information about celestial bodies
- **cached_events**: Stores astronomical events for bodies
- **search_history**: Tracks search queries for analytics

### Configuration

- `config.py`: Configuration settings loaded from environment variables
- `.env`: Environment-specific configuration (created from `.env.example`)

### Utilities

- `scripts/init_data.py`: Initialize the database with sample data
- `client/client.py`: Command-line client for testing and administration

### Deployment

- `Dockerfile`: Docker configuration for containerization
- `docker-compose.yml`: Docker Compose configuration
- `start.sh` / `start.bat`: Startup scripts for Unix and Windows

## Getting Started

1. Clone the repository
2. Run the appropriate startup script:
   - `./start.sh` on Linux/macOS
   - `start.bat` on Windows
3. Access the API at http://localhost:8000
4. View API documentation at http://localhost:8000/docs
