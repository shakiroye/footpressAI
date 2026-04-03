from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_openai_deployment: str
    azure_openai_emb_deployment: str

    azure_ai_language_endpoint: str
    azure_ai_language_key: str

    azure_ai_vision_endpoint: str
    azure_ai_vision_key: str

    azure_storage_conn_str: str
    azure_storage_container: str

    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index: str

    football_data_api_key: str = ""
    footpress_api_keys: str = "demo-key-footpress"

    class Config:
        env_file = ".env"

settings = Settings()
