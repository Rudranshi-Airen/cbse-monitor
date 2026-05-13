from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    target_url: str = "https://results.cbse.nic.in"
    poll_interval_seconds: int = 300  # 5 minutes
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notify_email: str = ""
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

settings = Settings()