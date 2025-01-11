from fastapi import FastAPI
from routers import events

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to NoClueAstronomy"}

app.include_router(events.router)
