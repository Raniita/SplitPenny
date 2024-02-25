import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    DEBUG: bool = True
    
    # Database Config
    POSTGRES_HOST : str = os.environ.get("POSTGRES_HOST", "db")
    POSTGRES_PORT : str = os.environ.get("POSTGRES_PORT", "5432")
    POSTGRES_DATABASE : str = os.environ.get("POSTGRES_DATABASE", "splitpenny")
    POSTGRES_USER : str = os.environ.get("POSTGRES_USER", "root")
    POSTGRES_PASSWORD : str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    DATABASE_URL : str = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    
class ProductionConfig(BaseConfig):
    DEBUG: bool = True
    
class TestingConfig(BaseConfig):
    DEBUG: bool = True
    
@lru_cache
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()

settings = get_settings()