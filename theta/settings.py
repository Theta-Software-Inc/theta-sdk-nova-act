from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
    api_key: Optional[str] = Field(default=None, alias="THETA_API_KEY", validation_alias="THETA_API_KEY")
    base_url: str = Field(default="http://osworld-alb-1747958937-924398482.us-west-1.elb.amazonaws.com")

settings = Settings()