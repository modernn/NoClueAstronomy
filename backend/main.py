from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_handler import verify_jwt
from routes import events

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Astronomical Events API"}

app.include_router(events.router, prefix="/events", dependencies=[Depends(verify_jwt)])
app.include_router(users.router, prefix="/users", tags=["Users"])