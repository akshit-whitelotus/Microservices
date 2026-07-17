## Database migrations

Create migration:

alembic revision --autogenerate -m "migration message"


Apply migrations:

alembic upgrade head