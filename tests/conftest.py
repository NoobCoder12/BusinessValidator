import pytest
import os

# Overriding env for test purpose
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["SENTRY_URL"] = ""

from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.main import app
from app.db.deps import get_db
from httpx import AsyncClient, ASGITransport

TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:5432/{settings.POSTGRES_DB}_test"

# @pytest.fixture provides context for the tests


@pytest.fixture
# Needs to be async because of asyncpg
async def test_db() -> AsyncSession:
    '''
    Creates clean database for each test.
    After completing database is removed.
    '''
    # Engine setup
    engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)

    # Session setup
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

    # Creating and dropping tables must be done through engine, not session
    # .begin() makes sure that transaction is atomic
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # run_sync - 'this method allows traditional synchronous SQLAlchemy functions to run within the context of an asyncio application'

    async with AsyncSessionLocal() as session:
        yield session

    # Clear database after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()  # Clear the enginge if no longer used


@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncClient:
    """
    TestClient FastAPI with test database.
    Used to test endpoints, simulates user's action.
    """
    # Function for overriding to test database
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db  # For test purpose switching real DB with TEST_DB

    # For endpoint testing client is needed
    # app=app means send a request through the app, not web
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as c:    # For test url can be random, httpx needs it
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def user_data():
    """
    Data for registration/JWT
    """
    return {
        "email": "test@email.com",
        "password": "PasswordTest.123!",
        "username": "tester123"
    }


@pytest.fixture
async def registered_user(
    client: AsyncClient,
    user_data: dict
):
    """
    Fixture for user registration.
    Pass as argument for silent POST, in code user_data may be used.
    """
    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def logged_user(
    client: AsyncClient,
    registered_user: dict,
    user_data: dict
):
    """
    Fixture for logged user header with JWT.
    """
    login_params = {
        # .get("email") may be used for email as username
        "username": user_data.get("username"),
        "password": user_data.get("password")
    }

    response = await client.post("/api/v1/auth/token", data=login_params)

    assert response.status_code == 200
    data = response.json()
    token = data.get("access_token")

    return {"Authorization": f"Bearer {token}"}

