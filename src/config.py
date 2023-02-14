from typing import Optional, List
from pydantic import BaseSettings


class Settings(BaseSettings):
    address_prompt_file: str = "prompts/address.txt"
    detailed_intent_prompt_file: str = "prompts/intent_v5_categories.txt"
    address_template: Optional[str] = None
    detailed_intent_template: Optional[str] = None
    geo_key: Optional[str] = None
    openai_keys: Optional[List[str]] = None
    address_max_tokens: int = 384
    detailed_intent_max_tokens: int = 100
    batch_size: int = 20
    geo_location: bool = False
    num_workers: int = 5
    engine: str = "afet-org"

    class Config:
        env_file = ".env"


    