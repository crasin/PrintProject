from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Cloud
    cloud_api_url: str
    store_api_key: str
    store_id: str

    # CUPS printer names — run `lpstat -p` on the Pi to find these
    photo_printer_name: str
    document_printer_name: str

    # Local temp storage — print-and-delete, never accumulates
    temp_dir: str = "/tmp/printjobs"

    # Heartbeat
    heartbeat_interval: int = 60


settings = Settings()
