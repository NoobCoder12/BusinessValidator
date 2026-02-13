from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_DB: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE: int
    
    REFRESH_TOKEN_KEY: str
    REFRESH_ACCESS_TOKEN_EXPIRE: int

    @property   # method is used as variable
    def DATABASE_URL(self) -> str:
        """
        Returns valid db url.
        Dynamically assembles the async database connection string 
        using individual PostgreSQL credentials.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:5432/{self.POSTGRES_DB}"

    # Shows where to find variables, defines behaviour while loading settings
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  # Prevents errors if .env contains variables not defined in this class


settings = Settings()   # To import it into different module