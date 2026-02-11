from fastapi import FastAPI
from app.api.v1.endpoints import auth

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])


@app.get("/")
def root():
    return {"message": "API is running"}