from functools import lru_cache
from app.core.database import get_db
from app.core.config import Settings, settings

@lru_cache()
def get_settings() -> Settings:
    return settings

# get_db is imported and can be used as a dependency directly
