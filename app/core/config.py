from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RFC 3164/5424 Syslog Parser"
    version: str = "2.0.0"
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()