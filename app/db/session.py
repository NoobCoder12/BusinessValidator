from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)     # echo shows SQL in terminal, future is for new methods

# Session factory
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
# expire_on_commit=False prevents errors while reading database
# autoflush=False no auto saving