from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from splitpenny.config import settings

def create_app() :
    app = FastAPI()
    
    print(f"Using {settings.DATABASE_URL}")
    
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