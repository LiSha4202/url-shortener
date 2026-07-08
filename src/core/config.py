from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DataBaseSettings(BaseSettings):
    url: str = "postgresql:///./app.db"
    echo: bool = False
    pool_pre_ping = True
    pool_size = 5
    max_overflow = 10
    autocommit = False
    autoflush = False


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    db: DataBaseSettings = DataBaseSettings()


settings = Settings()
