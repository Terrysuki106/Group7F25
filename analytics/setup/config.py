# sensor_pipeline/config.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    sampling_rate: int 
    missing_value_policy: str
    output_path: Path
    raw_path: Path
    db_enabled: bool
    timezone: str
    normal_digits: int = 3
    location_digits: int = 5
    reset_mode: bool
    db_folder: Path = Path("database")
    db_filename: str = "driving.db"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def db_path(self) -> Path:
        # ensure folder exists
        self.db_folder.mkdir(parents=True, exist_ok=True)
        return self.db_folder / self.db_filename

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"


def Initialize_configuration():
    cfg = Config() # type: ignore