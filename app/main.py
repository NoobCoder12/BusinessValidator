from fastapi import FastAPI, Request
import sentry_sdk
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import auth, business, status
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.logging import logger, setup_logging
from app.core.config import settings
import logging
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration

setup_logging()  # Logger starts with an app

# Creating logging integration for breadcrumbs
# "Explicit is better than implicit", these are default LogginIntegration() settings
sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR
)

sentry_sdk.init(
    dsn=settings.SENTRY_URL,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # Integrations are needed to have bigger scope during error
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
        RedisIntegration(),
        sentry_logging
    ],
    # TODO: change to 0.1 when traffic
    traces_sample_rate=1.0,     # Monitor all requests
    send_default_pii=True,      # Sends 'personal' user informations
    environment="development"
)


app = FastAPI()


logger.info("Application startup: Logging configured successfully")

app.state.limiter = limiter     # Adding limiter to app state
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)      # Handling exception for rate limit

logger.info("Limiter: configured successfully")


@app.exception_handler(Exception)
# FastAPI needs 2 args for exception handler
async def global_exception_handler(request: Request, exception: Exception):
    """
    Function for displaying error ID for User.
    Easier to track error in Sentry.
    """
    event_id = sentry_sdk.capture_exception(exception)   # Get exception and convert it to ID

    logger.error(f"Global error caught: {exception} | Error ID: {event_id}")    # Optional for local error logging

    return JSONResponse(
        status_code=500,
        content={
            "message": "An internal server error occurred",
            "error_id": event_id
        }
    )


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(business.router, prefix="/api/v1/business", tags=["Business Verification"])
app.include_router(status.router, prefix="/api/v1", tags=["Outer API health check"])


@app.get("/")
def root():
    return {"message": "API is running"}
