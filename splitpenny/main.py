from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
import logging

from splitpenny.config import settings

logger = logging.getLogger(__name__)

def create_app() :
    app = FastAPI()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info(f"Using {settings.DATABASE_URL}")
    
    # Register Tortoise ORM
    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["splitpenny.database.models"]},
        generate_schemas=True,
        add_exception_handlers=True
    )
     
    @app.get("/", include_in_schema=False)
    async def home():
        return f"hello wo11rld"
    
    return app
    
app = create_app()
