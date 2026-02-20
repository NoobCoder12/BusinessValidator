from fastapi import FastAPI
from app.api.v1.endpoints import auth, business, status
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.logging import logger, setup_logging

setup_logging()  # Logger starts with an app

app = FastAPI()

logger.info("Application startup: Logging configured successfully")

app.state.limiter = limiter     # Adding limiter to app state
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)      # Handling exception for rate limit

logger.info("Limiter: configured successfully")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(business.router, prefix="/api/v1/business", tags=["Business Verification"])
app.include_router(status.router, prefix="/api/v1", tags=["Outer API health check"])


@app.get("/")
def root():
    return {"message": "API is running"}
