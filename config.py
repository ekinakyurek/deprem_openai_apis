from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    address_prompt_file: str = "prompts/address.txt"
    intent_prompt_file: str = "prompts/intent_v2.txt"
    detailed_intent_prompt_file: str = "prompts/intent_v5.txt"
    detailed_intent_prompt_file_v2: str = "prompts/intent_v5_categories.txt"
    address_template: Optional[str] = None
    intent_template: Optional[str] = None
    detailed_intent_template: Optional[str] = None
    detailed_intent_template_v2: Optional[str] = None
    geo_key: Optional[str] = None
    address_max_tokens: int = 384
    intent_max_tokens: int = 100
    detailed_intent_max_tokens: int = 50
    detailed_intent_max_tokens_v2: int = 100
    batch_size: int = 20
    geo_location: bool = False
    num_workers: int = 5
    engine: str = "afet-org"

    class Config:
        env_file = ".env"


    