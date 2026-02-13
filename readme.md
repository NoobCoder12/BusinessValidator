ALEMBIC:

alembic revision --autogenerate -m "message"
alembic  upgrade head
uvicorn app.main:app --reload

openssl rand -hex 32

docker exec -it business_db_cont psql -U admin -d business_db