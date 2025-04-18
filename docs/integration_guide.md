# NoClueAstronomy API Integration Guide

This guide provides examples and best practices for integrating the NoClueAstronomy API into various applications.

## Table of Contents

- [REST API Integration](#rest-api-integration)
  - [JavaScript/Web Applications](#javascriptweb-applications)
  - [Python Applications](#python-applications)
  - [Mobile Applications](#mobile-applications)
- [Common Use Cases](#common-use-cases)
  - [Displaying Planet Information](#displaying-planet-information)
  - [Building a Moon Phase Calendar](#building-a-moon-phase-calendar)
  - [Creating a Celestial Event Tracker](#creating-a-celestial-event-tracker)
- [Performance Optimization](#performance-optimization)
  - [Using the Multiple Bodies Endpoint](#using-the-multiple-bodies-endpoint)
  - [Caching Strategies](#caching-strategies)
- [Error Handling](#error-handling)
- [Webhooks and Notifications (Future Feature)](#webhooks-and-notifications-future-feature)

## REST API Integration

### JavaScript/Web Applications

#### Using Fetch API

```javascript
// Example: Fetching information about Mars
async function getMarsInfo() {
  try {
    const response = await fetch('http://localhost:8000/bodies/mars');
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching Mars data:', error);
    throw error;
  }
}

// Example: Searching for celestial bodies
async function searchBodies(term) {
  try {
    const response = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ term }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('Error searching for bodies:', error);
    throw error;
  }
}

// Example: Getting upcoming moon events
async function getMoonEvents() {
  try {
    const today = new Date().toISOString().split('T')[0];
    const nextMonth = new Date();
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    const nextMonthStr = nextMonth.toISOString().split('T')[0];
    
    const response = await fetch(
      `http://localhost:8000/events/moon?start_date=${today}&end_date=${nextMonthStr}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.events;
  } catch (error) {
    console.error('Error fetching moon events:', error);
    throw error;
  }
}
```

#### Using Axios

```javascript
import axios from 'axios';

// Create an API client
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000,
});

// Example: Fetching multiple bodies at once
async function getSolarSystemPlanets() {
  try {
    const response = await apiClient.get(
      '/bodies/multiple?body_ids=mercury,venus,earth,mars,jupiter,saturn,uranus,neptune'
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching solar system planets:', error);
    throw error;
  }
}

// Example: Error handling with rate limits
async function fetchWithRateLimitHandling(url) {
  try {
    const response = await apiClient.get(url);
    
    // Get rate limit information from headers
    const rateLimit = response.headers['x-ratelimit-limit'];
    const rateLimitRemaining = response.headers['x-ratelimit-remaining'];
    
    console.log(`Rate limit: ${rateLimitRemaining}/${rateLimit} remaining`);
    
    return response.data;
  } catch (error) {
    if (error.response && error.response.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 10;
      console.warn(`Rate limit exceeded. Retrying after ${retryAfter} seconds.`);
      
      // Wait and retry
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      return fetchWithRateLimitHandling(url);
    }
    
    console.error('API request failed:', error);
    throw error;
  }
}
```

### Python Applications

#### Using the Requests Library

```python
import requests
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

def get_body_info(body_id, force_refresh=False):
    """Get information about a specific celestial body"""
    params = {"force_refresh": "true" if force_refresh else "false"}
    response = requests.get(f"{API_URL}/bodies/{body_id}", params=params)
    
    response.raise_for_status()  # Raise exception for HTTP errors
    return response.json()

def search_bodies(query):
    """Search for celestial bodies by name"""
    response = requests.post(f"{API_URL}/search", json={"term": query})
    
    response.raise_for_status()
    return response.json()["results"]

def get_upcoming_events(body_id, days=30):
    """Get upcoming events for a celestial body"""
    today = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    params = {
        "start_date": today,
        "end_date": end_date
    }
    
    response = requests.get(f"{API_URL}/events/{body_id}", params=params)
    
    response.raise_for_status()
    return response.json()["events"]
```

#### Creating a Python Client Class

```python
import requests
import time
from datetime import datetime, timedelta

class NoClueAstronomyClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _handle_rate_limits(self, response):
        """Handle rate limit headers and return remaining limits"""
        limit = response.headers.get("X-RateLimit-Limit")
        remaining = response.headers.get("X-RateLimit-Remaining")
        
        if limit and remaining:
            return int(remaining), int(limit)
        return None, None
    
    def get_body(self, body_id, force_refresh=False):
        """Get information about a specific celestial body"""
        params = {"force_refresh": "true" if force_refresh else "false"}
        response = self.session.get(f"{self.base_url}/bodies/{body_id}", params=params)
        
        # Handle rate limits
        remaining, limit = self._handle_rate_limits(response)
        if remaining is not None and remaining < 5:
            print(f"Warning: API rate limit approaching ({remaining}/{limit} remaining)")
        
        response.raise_for_status()
        return response.json()
    
    def get_multiple_bodies(self, body_ids, force_refresh=False):
        """Get information about multiple celestial bodies"""
        if isinstance(body_ids, list):
            body_ids = ",".join(body_ids)
        
        params = {
            "body_ids": body_ids,
            "force_refresh": "true" if force_refresh else "false"
        }
        
        response = self.session.get(f"{self.base_url}/bodies/multiple", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_events(self, body_id, start_date=None, end_date=None):
        """Get events for a specific celestial body"""
        params = {}
        
        if start_date:
            params["start_date"] = start_date
        
        if end_date:
            params["end_date"] = end_date
        
        response = self.session.get(f"{self.base_url}/events/{body_id}", params=params)
        response.raise_for_status()
        return response.json()
    
    def search(self, query):
        """Search for celestial bodies by name"""
        response = self.session.post(f"{self.base_url}/search", json={"term": query})
        response.raise_for_status()
        return response.json()["results"]
    
    def get_cache_stats(self):
        """Get statistics about the cache"""
        response = self.session.get(f"{self.base_url}/cache/stats")
        response.raise_for_status()
        return response.json()
    
    def clear_cache(self):
        """Clear all cached data"""
        response = self.session.delete(f"{self.base_url}/cache/clear")
        response.raise_for_status()
        return response.json()
    
    def check_health(self):
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/health")
        return response.status_code == 200, response.json()
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

### Mobile Applications

For mobile applications, you can use standard HTTP clients provided by each platform:

#### iOS (Swift) Example

```swift
import Foundation

class AstronomyAPIClient {
    let baseURL = "http://localhost:8000"
    
    func getBody(id: String, completion: @escaping (Result<[String: Any], Error>) -> Void) {
        let url = URL(string: "\(baseURL)/bodies/\(id)")!
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "AstronomyAPI", code: 0, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }
            
            do {
                if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                    completion(.success(json))
                } else {
                    completion(.failure(NSError(domain: "AstronomyAPI", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid JSON format"])))
                }
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}
```

#### Android (Kotlin) Example

```kotlin
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.io.IOException

class AstronomyApiClient(private val baseUrl: String = "http://localhost:8000") {
    private val client = OkHttpClient()
    
    fun getBody(bodyId: String): JSONObject {
        val request = Request.Builder()
            .url("$baseUrl/bodies/$bodyId")
            .build()
            
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Unexpected response: ${response.code}")
            }
            
            val responseBody = response.body?.string() ?: throw IOException("Empty response body")
            return JSONObject(responseBody)
        }
    }
}
```

## Common Use Cases

### Displaying Planet Information

```javascript
// Example: Creating a planet information component
async function displayPlanetInfo(planetId, elementId) {
  try {
    const planetData = await fetch(`http://localhost:8000/bodies/${planetId}`).then(res => res.json());
    
    const container = document.getElementById(elementId);
    if (!container) return;
    
    // Extract position information
    const position = planetData.data.position;
    const extraInfo = planetData.data.extraInfo || {};
    
    // Create HTML content
    container.innerHTML = `
      <h2>${planetData.name}</h2>
      <div class="info-section">
        <h3>Current Position</h3>
        <p>Right Ascension: ${position.equatorial.rightAscension.string}</p>
        <p>Declination: ${position.equatorial.declination.string}</p>
        <p>Constellation: ${position.constellation.name}</p>
      </div>
      <div class="info-section">
        <h3>Additional Information</h3>
        <p>Magnitude: ${extraInfo.magnitude || 'N/A'}</p>
        <p>Elongation: ${extraInfo.elongation || 'N/A'}</p>
      </div>
      <div class="meta">
        <p class="last-updated">Last updated: ${new Date(planetData.last_updated).toLocaleString()}</p>
        <p class="cached">${planetData.cached ? 'Loaded from cache' : 'Freshly loaded'}</p>
      </div>
    `;
  } catch (error) {
    console.error(`Error displaying planet info for ${planetId}:`, error);
  }
}
```

### Building a Moon Phase Calendar

```javascript
// Example: Creating a moon phase calendar for the current month
async function createMoonPhaseCalendar(containerId) {
  try {
    // Get the current date and end of month
    const today = new Date();
    const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    // Format dates for API request
    const startDate = today.toISOString().split('T')[0];
    const endDate = endOfMonth.toISOString().split('T')[0];
    
    // Fetch moon events
    const response = await fetch(
      `http://localhost:8000/events/moon?start_date=${startDate}&end_date=${endDate}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    const events = data.events;
    
    // Create the calendar HTML
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Map event types to emoji/icons
    const phaseIcons = {
      'new_moon': '🌑',
      'first_quarter': '🌓',
      'full_moon': '🌕',
      'last_quarter': '🌗'
    };
    
    // Create calendar entries
    let calendarHTML = '<div class="moon-calendar">';
    calendarHTML += '<h2>Moon Phases This Month</h2>';
    calendarHTML += '<ul class="phases-list">';
    
    events.forEach(event => {
      if (!event.cells || !event.cells[0] || !event.cells[0].date) return;
      
      const eventDate = new Date(event.cells[0].date);
      const phaseName = event.entry.name;
      const phaseId = event.entry.id;
      const icon = phaseIcons[phaseId] || '🌙';
      
      calendarHTML += `
        <li class="phase-item">
          <span class="phase-icon">${icon}</span>
          <span class="phase-name">${phaseName}</span>
          <span class="phase-date">${eventDate.toLocaleDateString()}</span>
        </li>
      `;
    });
    
    calendarHTML += '</ul></div>';
    container.innerHTML = calendarHTML;
    
  } catch (error) {
    console.error('Error creating moon phase calendar:', error);
  }
}
```

### Creating a Celestial Event Tracker

```python
import datetime
import prettytable

class CelestialEventTracker:
    """Track upcoming astronomical events for multiple celestial bodies"""
    
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        # List of bodies to track
        self.bodies_to_track = ["moon", "mars", "jupiter", "saturn"]
    
    def get_upcoming_events(self, days=90):
        """Get upcoming events for all tracked bodies"""
        import requests
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        
        all_events = []
        
        for body_id in self.bodies_to_track:
            try:
                response = requests.get(
                    f"{self.api_url}/events/{body_id}",
                    params={"start_date": today, "end_date": end_date}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for event in data["events"]:
                        event_date = None
                        event_text = None
                        
                        # Extract date and text from cells
                        for cell in event.get("cells", []):
                            if "date" in cell:
                                event_date = cell["date"]
                            if "text" in cell:
                                event_text = cell["text"]
                        
                        if event_date:
                            all_events.append({
                                "body": data["body_id"],
                                "event": event["entry"]["name"],
                                "date": event_date,
                                "text": event_text or "",
                            })
            except Exception as e:
                print(f"Error fetching events for {body_id}: {str(e)}")
        
        # Sort events by date
        all_events.sort(key=lambda x: x["date"])
        
        return all_events
    
    def print_event_table(self, days=90):
        """Print events in a formatted table"""
        events = self.get_upcoming_events(days)
        
        if not events:
            print("No upcoming events found.")
            return
        
        table = prettytable.PrettyTable()
        table.field_names = ["Date", "Body", "Event"]
        
        for event in events:
            # Format the date
            date_obj = datetime.datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
            formatted_date = date_obj.strftime("%Y-%m-%d")
            
            table.add_row([
                formatted_date,
                event["body"].capitalize(),
                event["event"]
            ])
        
        print(f"Upcoming Celestial Events (Next {days} Days)")
        print(table)
```

## Performance Optimization

### Using the Multiple Bodies Endpoint

For applications that need data about several celestial bodies at once, use the multiple bodies endpoint to reduce the number of API calls:

```javascript
// Instead of making multiple requests:
const earth = await fetch('/bodies/earth').then(res => res.json());
const mars = await fetch('/bodies/mars').then(res => res.json());
const jupiter = await fetch('/bodies/jupiter').then(res => res.json());

// Make a single request:
const bodies = await fetch('/bodies/multiple?body_ids=earth,mars,jupiter').then(res => res.json());
const [earth, mars, jupiter] = bodies;
```

### Caching Strategies

The API already implements server-side caching, but clients can implement additional caching:

```javascript
// Example: Simple client-side caching
const cache = new Map();
const CACHE_TTL = 3600000; // 1 hour in milliseconds

async function getBodyWithCache(bodyId) {
  const cacheKey = `body_${bodyId}`;
  
  // Check if we have a valid cache entry
  if (cache.has(cacheKey)) {
    const cachedData = cache.get(cacheKey);
    if (Date.now() - cachedData.timestamp < CACHE_TTL) {
      console.log(`Using cached data for ${bodyId}`);
      return cachedData.data;
    }
  }
  
  // Fetch fresh data
  const response = await fetch(`http://localhost:8000/bodies/${bodyId}`);
  const data = await response.json();
  
  // Update cache
  cache.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
  
  return data;
}
```

## Error Handling

```javascript
// Example: Robust error handling for API requests
async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    // Handle HTTP error statuses
    if (!response.ok) {
      const errorText = await response.text();
      let errorInfo;
      
      try {
        // Try to parse error as JSON
        errorInfo = JSON.parse(errorText);
      } catch (e) {
        // If not JSON, use raw text
        errorInfo = { detail: errorText };
      }
      
      // Handle specific error codes
      switch (response.status) {
        case 404:
          throw new Error(`Resource not found: ${errorInfo.detail || 'Not found'}`);
        case 429:
          const retryAfter = response.headers.get('Retry-After') || 10;
          throw new Error(`Rate limit exceeded. Try again after ${retryAfter} seconds.`);
        case 502:
          throw new Error('External astronomy API error. Please try again later.');
        default:
          throw new Error(`API error (${response.status}): ${errorInfo.detail || 'Unknown error'}`);
      }
    }
    
    return await response.json();
  } catch (error) {
    // Handle network errors
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
      throw new Error('Network error. Please check your internet connection.');
    }
    
    // Re-throw API errors
    throw error;
  }
}
```

## Webhooks and Notifications (Future Feature)

In future versions, the API may support webhooks to notify applications about upcoming astronomical events:

```python
# Example: Registering for event notifications (conceptual, not yet implemented)
import requests

def register_webhook(event_type, callback_url, api_key):
    """Register a webhook for astronomical event notifications"""
    response = requests.post(
        "http://localhost:8000/webhooks/register",
        json={
            "event_type": event_type,  # e.g., "full_moon", "solar_eclipse"
            "callback_url": callback_url,
            "api_key": api_key
        }
    )
    
    response.raise_for_status()
    return response.json()
```

This integration guide provides a starting point for incorporating the NoClueAstronomy API into your applications. For detailed API documentation, refer to the [API Documentation](http://localhost:8000/docs).
