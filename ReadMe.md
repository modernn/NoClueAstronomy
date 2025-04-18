# NoClueAstronomy API

A FastAPI-based application that provides a caching layer for astronomical data from the [Astronomy API](https://astronomyapi.com). This project allows you to query information about celestial bodies and astronomical events while minimizing external API calls through efficient caching.

## Features

- **Body Information**: Fetch and cache detailed information about celestial bodies
- **Astronomical Events**: Retrieve upcoming astronomical events for specific bodies
- **Multi-Body Queries**: Fetch data for multiple celestial bodies in a single request
- **Search**: Search for celestial bodies by name
- **Caching**: Automated caching with configurable expiration to minimize external API calls
- **Search History**: Track search queries for analytics
- **Rate Limiting**: Protect the API from abuse with configurable rate limiting
- **Admin Functions**: Cache statistics and management

## Prerequisites

- Python 3.8 or higher
- [Astronomy API](https://astronomyapi.com) credentials (Application ID and Secret)
- Docker and Docker Compose (optional, for containerized deployment)

## Quick Start

### Using the Startup Scripts

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/noclue-astronomy-api.git
   cd noclue-astronomy-api
   ```

2. Run the startup script:
   - On Linux/macOS:
     ```bash
     chmod +x start.sh
     ./start.sh
     ```
   - On Windows:
     ```
     start.bat
     ```

3. The script will:
   - Create a virtual environment
   - Install dependencies
   - Create a `.env` file (if it doesn't exist)
   - Initialize the database with sample data
   - Start the API server

4. Edit the `.env` file to set your Astronomy API credentials.

5. Access the API at http://localhost:8000

6. View API documentation at http://localhost:8000/docs

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/noclue-astronomy-api.git
   cd noclue-astronomy-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Astronomy API credentials:
   ```
   ASTRONOMY_APP_ID=your_app_id
   ASTRONOMY_APP_SECRET=your_app_secret
   ```

4. Initialize the database:
   ```bash
   python -m scripts.init_data
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

### Docker Deployment

1. Create a `.env` file with your Astronomy API credentials:
   ```
   ASTRONOMY_APP_ID=your_app_id
   ASTRONOMY_APP_SECRET=your_app_secret
   ```

2. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

## API Reference

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

### Main Endpoints

- `GET /bodies/{body_id}` - Get information about a specific celestial body
- `GET /bodies/multiple` - Get information about multiple celestial bodies
- `GET /events/{body_id}` - Get astronomical events for a specific celestial body
- `GET /bodies` - List all available celestial bodies
- `POST /search` - Search for celestial bodies by name
- `GET /search/history` - Get recent search history
- `GET /cache/stats` - Get statistics about the cache
- `DELETE /cache/clear` - Clear all cached data
- `GET /health` - Check API health status

## Client Utility

A command-line client utility is included for easier interaction with the API:

```bash
# Get information about a specific body
python client.py body mars

# Get events for a specific body in a date range
python client.py events moon --start 2025-04-16 --end 2025-05-16

# Get information about multiple bodies at once
python client.py body mars,moon,jupiter

# List all available bodies
python client.py list

# Search for bodies
python client.py search mars

# View cache statistics
python client.py stats

# Clear the cache
python client.py clear-cache
```

## Configuration Options

The API can be configured using environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `ASTRONOMY_APP_ID` | Astronomy API Application ID | - |
| `ASTRONOMY_APP_SECRET` | Astronomy API Application Secret | - |
| `DATABASE_URL` | SQLite database URL | `sqlite:///./data/astronomy.db` |
| `CACHE_EXPIRATION_HOURS` | Hours before cached data expires | `24` |
| `RATE_LIMIT` | Maximum requests per minute | `60` |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | `60` |
| `RATE_LIMIT_BLOCK_TIME` | Block time after exceeding rate limit (seconds) | `300` |
| `API_LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` |

## Data Structure

The API uses SQLite to store cached data with the following tables:

- `cached_bodies` - Stores information about celestial bodies
- `cached_events` - Stores astronomical events for bodies
- `search_history` - Tracks search queries for analytics

## Cache Management

By default, cached data expires after 24 hours. You can force a refresh by adding the `force_refresh=true` parameter to API requests or using the `--refresh` flag with the client utility.

## Rate Limiting

The API includes rate limiting to prevent abuse:

- **Default Rate Limit**: 60 requests per minute
- **Window Size**: 60 seconds (sliding window)
- **Block Time**: 5 minutes after exceeding the rate limit

Rate limit information is included in response headers:
- `X-RateLimit-Limit` - Maximum requests allowed per minute
- `X-RateLimit-Remaining` - Remaining requests in the current window

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - The request was successful
- `400 Bad Request` - The request was invalid
- `404 Not Found` - The requested resource was not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - An error occurred on the server
- `502 Bad Gateway` - Error communicating with the Astronomy API
- `503 Service Unavailable` - The service is currently unavailable

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for a detailed overview of the project organization.

## Testing

Run the tests using pytest:

```bash
pytest
```

Or run a specific test:

```bash
pytest tests/test_api.py -v
```

## Development

### Adding New Features

1. Create feature branches from `main`
2. Write tests for new functionality
3. Implement the feature
4. Create a pull request

### Coding Standards

- Follow PEP 8 for Python code
- Add docstrings to all functions and classes
- Write tests for new functionality

## Deployment

### Heroku Deployment

```bash
heroku create noclue-astronomy-api
heroku config:set ASTRONOMY_APP_ID=your_app_id
heroku config:set ASTRONOMY_APP_SECRET=your_app_secret
git push heroku main
```

### AWS Deployment

See [docs/aws-deployment.md](docs/aws-deployment.md) for detailed AWS deployment instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Astronomy API](https://astronomyapi.com) for providing the astronomical data
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM
# NoClueAstronomy API

A FastAPI-based application that provides a caching layer for astronomical data from the Astronomy API. This project allows you to query information about celestial bodies and astronomical events while minimizing external API calls through efficient caching.

## Features

- **Body Information**: Fetch and cache detailed information about celestial bodies
- **Astronomical Events**: Retrieve upcoming astronomical events for specific bodies
- **Search**: Search for celestial bodies by name
- **Caching**: Automated caching with configurable expiration to minimize external API calls
- **Search History**: Track search queries for analytics
- **Admin Functions**: Cache statistics and management

## Prerequisites

- Python 3.8 or higher
- [Astronomy API](https://astronomyapi.com) credentials (Application ID and Secret)
- Docker and Docker Compose (optional, for containerized deployment)

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/noclue-astronomy-api.git
   cd noclue-astronomy-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export ASTRONOMY_APP_ID="your_app_id"
   export ASTRONOMY_APP_SECRET="your_app_secret"
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

### Docker Deployment

1. Create a `.env` file with your Astronomy API credentials:
   ```
   ASTRONOMY_APP_ID=your_app_id
   ASTRONOMY_APP_SECRET=your_app_secret
   ```

2. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

## API Reference

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

### Main Endpoints

- `GET /bodies/{body_id}` - Get information about a specific celestial body
- `GET /events/{body_id}` - Get astronomical events for a specific celestial body
- `GET /bodies` - List all available celestial bodies
- `POST /search` - Search for celestial bodies by name
- `GET /search/history` - Get recent search history
- `GET /cache/stats` - Get statistics about the cache
- `DELETE /cache/clear` - Clear all cached data

## Client Utility

A command-line client utility is included for easier interaction with the API:

```bash
# Get information about a specific body
python client.py body mars

# Get events for a specific body in a date range
python client.py events moon --start 2025-04-16 --end 2025-05-16

# List all available bodies
python client.py list

# Search for bodies
python client.py search mars

# View cache statistics
python client.py stats

# Clear the cache
python client.py clear-cache
```

## Data Structure

The API uses SQLite to store cached data with the following tables:

- `cached_bodies` - Stores information about celestial bodies
- `cached_events` - Stores astronomical events for bodies
- `search_history` - Tracks search queries for analytics

## Cache Management

By default, cached data expires after 24 hours. You can force a refresh by adding the `force_refresh=true` parameter to API requests or using the `--refresh` flag with the client utility.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project uses the [Astronomy API](https://astronomyapi.com) for astronomical data.
