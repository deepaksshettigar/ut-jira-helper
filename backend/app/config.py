from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Jira Settings
    jira_server: str = ""
    jira_username: str = ""
    jira_api_token: str = ""
    jira_project_key: str = ""
    
    # LLM Settings
    llm_model_repo: str = ""
    llm_model_filename: str = ""
    llm_model_path: str = ""
    llm_context_size: int = 4096
    llm_max_tokens: int = 512
    llm_temperature: float = 0.7
    
    # App Settings
    app_debug: bool = False
    app_log_level: str = "info"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()

print("Loaded LLM_MODEL_PATH from settings:", settings.llm_model_path)
print("Loaded LLM_MODEL_PATH from os.environ:", os.getenv("LLM_MODEL_PATH"))
print("Current working directory:", os.getcwd())