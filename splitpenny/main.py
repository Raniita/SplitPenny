from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from contextlib import asynccontextmanager
import logging

from splitpenny.config import settings
from splitpenny.database.models import Base

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionFactory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
logger = logging.getLogger(__name__)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def get_session_db():
    async_session = AsyncSessionFactory()
    try:
        yield async_session
    finally:
        await async_session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init SQLAlchemyModels
    await init_models()
    yield
    # Clean up the ML models and release the resources
    print("nothing")

def create_app() :
    app = FastAPI(lifespan=lifespan)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logging.basicConfig(level=logging.INFO, handlers=[
        logging.StreamHandler()])  
    
    logger.info(f"Using {settings.DATABASE_URL}")
    
    # Routers!
    from splitpenny.routers.user import router as user_router
    from splitpenny.routers.bucket import router as bucket_router
    from splitpenny.routers.auth import router as auth_router
    app.include_router(user_router)
    app.include_router(bucket_router)
    app.include_router(auth_router)
    
    @app.get("/", include_in_schema=False)
    async def home():
        return f"hello wo11rld"
    
    return app
    
app = create_app()
