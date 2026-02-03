"""Configuration management using pydantic-settings."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram Bot
    telegram_bot_token: str
    telegram_webhook_url: str | None = None
    bot_name: str = "BarinyaBot"
    webapp_url: str = "https://barinia.sweethome38.keenetic.pro/"

    
    # Database
    database_url: str
    
    # Admin
    admin_telegram_ids: int | None = None
    reviews_channel_id: int | None = None
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    

    path_menu: str = "/data/menu.json"

    # Google Sheets (optional)
    google_sheets_credentials_file: str | None = None
    google_sheets_spreadsheet_id: str | None = None
    google_sheets_range: str = "Menu!A2:F"

    #JWT
    jwt_secret_key: str
    
    #Redis 
    session_ttl: int = 7200
    session_max_lifetime: int = 86400
    redis_host: str = 'redis'
    redis_port: int = 6783
    redis_password: str = "some_passw9832983"

    # Logging
    log_level: str = "DEBUG"
    log_to_file: bool = True
    log_max_size_mb: int = 10
    log_backup_count: int = 5

    
    @property
    def admin_ids_list(self) -> list[int]:
        """Parse admin telegram IDs from comma-separated string."""
        if not self.admin_telegram_ids:
            return []
        return [int(id.strip()) for id in self.admin_telegram_ids.split(",") if id.strip()]


# Global settings instance
settings = Settings()
