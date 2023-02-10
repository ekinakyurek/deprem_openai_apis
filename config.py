from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    address_prompt_file: str = "prompts/address.txt"
    intent_prompt_file: str = "prompts/intent_v2.txt"
    address_template: Optional[str] = None
    intent_template: Optional[str] = None
    geo_key: Optional[str] = None
    address_max_tokens: int = 384
    intent_max_tokens: int = 100
    batch_size: int = 20
    geo_location: bool = True
    num_workers: int = 5
    engine: str = "code-cushman-001"

    class Config:
        env_file = ".env"


    