# NoClueAstronomy API Documentation

## Introduction

The NoClueAstronomy API provides a caching layer on top of the [Astronomy API](https://astronomyapi.com) and [NASA API](https://api.nasa.gov), allowing you to retrieve astronomical data while minimizing external API calls. This API is designed to be efficient, easy to use, and suitable for both web and mobile applications.

## Authentication

This API doesn't require authentication for basic usage. However, rate limiting is enforced to prevent abuse:

- **Rate Limit**: 60 requests per minute by default
- **Enforcement**: Based on client IP address and optional API key
- **Block Time**: 5 minutes after exceeding the rate limit

The following headers are included in responses to help you track your rate limit status:

- `X-RateLimit-Limit`: Maximum number of requests allowed per minute
- `X-RateLimit-Remaining`: Number of requests remaining in the current window

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your domain.

## Endpoints

### Celestial Bodies

#### Get a single celestial body

```
GET /bodies/{body_id}
```

Retrieves detailed information about a specific celestial body.

**Path Parameters**:
- `body_id` (string, required): ID of the celestial body (e.g., "mars", "moon")

**Query Parameters**:
- `force_refresh` (boolean, optional): Force refresh cached data. Default: false
- `preferred_source` (string, optional): Preferred data source ('astronomy_api', 'nasa_api', etc.)
- `latitude` (number, optional): Observer latitude in degrees. Default: 0
- `longitude` (number, optional): Observer longitude in degrees. Default: 0
- `elevation` (number, optional): Observer elevation in meters. Default: 0

**Example Request**:
```
GET /bodies/mars?latitude=40.7128&longitude=-74.0060&elevation=10&preferred_source=nasa_api
```

**Example Response**:
```json
{
  "id": "mars",
  "name": "Mars",
  "data": {
    "position": {
      "equatorial": {
        "rightAscension": {
          "hours": "10.5",
          "string": "10h 30m 0s"
        },
        "declination": {
          "degrees": "15.2",
          "string": "15° 12' 0\""
        }
      },
      "constellation": {
        "id": "leo",
        "short": "Leo",
        "name": "Leo"
      }
    },
    "extraInfo": {
      "magnitude": 1.2,
      "elongation": 45.8
    }
  },
  "cached": true,
  "last_updated": "2025-04-16T12:34:56.789Z",
  "source": "nasa_api"
}
```

#### Get multiple celestial bodies

```
GET /bodies/multiple
```

Retrieves detailed information about multiple celestial bodies in a single request.

**Query Parameters**:
- `body_ids` (string, required): Comma-separated list of body IDs (e.g., "mars,moon,jupiter")
- `force_refresh` (boolean, optional): Force refresh cached data. Default: false
- `preferred_source` (string, optional): Preferred data source ('astronomy_api', 'nasa_api', etc.)

**Example Request**:
```
GET /bodies/multiple?body_ids=mars,moon,jupiter&preferred_source=astronomy_api
```

**Example Response**:
```json
[
  {
    "id": "mars",
    "name": "Mars",
    "data": { /* Mars data */ },
    "cached": true,
    "last_updated": "2025-04-16T12:34:56.789Z",
    "source": "astronomy_api"
  },
  {
    "id": "moon",
    "name": "Moon",
    "data": { /* Moon data */ },
    "cached": true,
    "last_updated": "2025-04-16T12:34:56.789Z",
    "source": "astronomy_api"
  },
  {
    "id": "jupiter",
    "name": "Jupiter",
    "data": { /* Jupiter data */ },
    "cached": true,
    "last_updated": "2025-04-16T12:34:56.789Z",
    "source": "astronomy_api"
  }
]
```

#### List available celestial bodies

```
GET /bodies
```

Lists all available celestial bodies from the astronomy data providers.

**Query Parameters**:
- `preferred_source` (string, optional): Preferred data source ('astronomy_api', 'nasa_api', etc.)

**Example Response**:
```json
{
  "bodies": [
    {
      "id": "earth",
      "name": "Earth",
      "bodyType": "Planet"
    },
    {
      "id": "mars",
      "name": "Mars",
      "bodyType": "Planet"
    },
    /* ... */
  ]
}
```

### Astronomical Events

#### Get events for a specific celestial body

```
GET /events/{body_id}
```

Retrieves astronomical events for a specific celestial body within a date range.

**Path Parameters**:
- `body_id` (string, required): ID of the celestial body (e.g., "mars", "moon")

**Query Parameters**:
- `start_date` (string, optional): Start date in YYYY-MM-DD format. Default: current date
- `end_date` (string, optional): End date in YYYY-MM-DD format. Default: current date + 30 days
- `force_refresh` (boolean, optional): Force refresh cached data. Default: false
- `preferred_source` (string, optional): Preferred data source ('astronomy_api', 'nasa_api', etc.)
- `latitude` (number, optional): Observer latitude in degrees. Default: 0
- `longitude` (number, optional): Observer longitude in degrees. Default: 0
- `elevation` (number, optional): Observer elevation in meters. Default: 0

**Example Request**:
```
GET /events/moon?start_date=2025-04-16&end_date=2025-05-16&preferred_source=astronomy_api
```

**Example Response**:
```json
{
  "body_id": "moon",
  "events": [
    {
      "entry": {
        "id": "new_moon",
        "name": "New Moon"
      },
      "cells": [
        {
          "date": "2025-04-20T00:00:00.000Z",
          "text": "April 20, 2025"
        }
      ]
    },
    {
      "entry": {
        "id": "first_quarter",
        "name": "First Quarter"
      },
      "cells": [
        {
          "date": "2025-04-27T00:00:00.000Z",
          "text": "April 27, 2025"
        }
      ]
    },
    /* ... */
  ],
  "cached": true,
  "last_updated": "2025-04-16T12:34:56.789Z",
  "source": "astronomy_api"
}
```

### Search

#### Search for celestial bodies

```
POST /search
```

Searches for celestial bodies by name.

**Query Parameters**:
- `preferred_source` (string, optional): Preferred data source ('astronomy_api', 'nasa_api', etc.)

**Request Body**:
```json
{
  "term": "mar"
}
```

**Example Response**:
```json
{
  "results": [
    {
      "id": "mars",
      "name": "Mars",
      "bodyType": "Planet"
    }
  ]
}
```

#### Get search history

```
GET /search/history
```

Gets recent search history.

**Query Parameters**:
- `limit` (integer, optional): Number of history items to retrieve. Default: 10

**Example Response**:
```json
{
  "history": [
    {
      "query": "mars",
      "timestamp": "2025-04-16T12:34:56.789Z"
    },
    {
      "query": "moon",
      "timestamp": "2025-04-16T12:30:00.000Z"
    }
  ]
}
```

### Administration

#### Get cache statistics

```
GET /cache/stats
```

Gets statistics about the cache.

**Example Response**:
```json
{
  "bodies_cached": 10,
  "events_cached": 25,
  "searches_recorded": 50,
  "oldest_body_cache": "2025-04-15T00:00:00.000Z",
  "oldest_event_cache": "2025-04-15T00:00:00.000Z"
}
```

#### Clear cache

```
DELETE /cache/clear
```

Clears all cached data.

**Query Parameters**:
- `clear_search_history` (boolean, optional): Whether to also clear search history. Default: false

**Example Response**:
```json
{
  "message": "Cache cleared successfully",
  "bodies_cleared": 10,
  "events_cleared": 25,
  "search_history_cleared": 0
}
```

#### Health check

```
GET /health
```

Checks the health of the API and its dependencies.

**Example Response**:
```json
{
  "status": "ok",
  "database": "ok",
  "apis": {
    "astronomy_api": true,
    "nasa_api": true
  },
  "time": "2025-04-16T12:34:56.789Z",
  "version": "1.0.0"
}
```

#### API Information

```
GET /
```

Gets basic API information.

**Example Response**:
```json
{
  "name": "NoClueAstronomy API",
  "description": "An API that queries and caches astronomical data from various sources",
  "version": "1.0.0",
  "documentation": "/docs",
  "status": "/health"
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK`: The request was successful
- `400 Bad Request`: The request was invalid
- `404 Not Found`: The requested resource was not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: An error occurred on the server
- `502 Bad Gateway`: Error communicating with external APIs
- `503 Service Unavailable`: The service is currently unavailable
- `504 Gateway Timeout`: Timeout while communicating with external APIs

Error responses include a `detail` field with a description of the error:

```json
{
  "detail": "Error message here"
}
```

## Caching

By default, cached data expires after 24 hours. You can force a refresh by adding the `force_refresh=true` parameter to API requests.

## Rate Limiting

If you exceed the rate limit, you'll receive a `429 Too Many Requests` response with a `Retry-After` header indicating the number of seconds to wait before retrying.

The rate limiting is implemented using a sliding window algorithm that tracks requests over time.

## Data Sources

The API can retrieve data from multiple sources:

- **astronomy_api**: Default source, provides comprehensive celestial body data
- **nasa_api**: Alternative source with additional NASA-specific information

You can specify your preferred source using the `preferred_source` parameter in your requests.
