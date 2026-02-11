from app.db.session import AsyncSessionLocal


async def get_db():
    # async with will close session after finish
    async with AsyncSessionLocal() as session:
        yield session
