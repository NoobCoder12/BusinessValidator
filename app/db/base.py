from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base Class for all SQLAlchemy models in project.
    Thanks to inheritation, SQLAlchemy register every created table,
    like User for example.
    Class created to collect all models.
    """
    pass
