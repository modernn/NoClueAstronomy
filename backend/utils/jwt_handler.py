import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from jwt import PyJWTError

JWT_SECRET = "your-secret-key"

def create_jwt(data: dict):
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")

def verify_jwt(token: str = Security(HTTPBearer())):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
