import secrets
from datetime import datetime

# Generate a URL-safe key
key = secrets.token_urlsafe(64)

# Get the current timestamp and format it
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Create a filename with the timestamp
filename = f"key_{timestamp}.txt"

# Save the key to a new text file
with open(filename, 'w') as file:
    file.write(key)

print(f"Key saved to {filename}")
