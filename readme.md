ALEMBIC:

alembic revision --autogenerate -m "message"
alembic  upgrade head
uvicorn app.main:app --reload

openssl rand -hex 32