from pydantic_settings import BaseSettings

# Configuration settings
class Settings(BaseSettings):
    domain: str = "localhost"
    enable_https: bool = False

    class Config:
        env_file = ".env"

# Dependency
def get_settings():
    return Settings()
