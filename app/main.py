from fastapi import FastAPI

def create_app() :
    app = FastAPI()
     
    @app.get("/", include_in_schema=False)
    async def home():
        return f"asdasaaad"
    
    return app
    
app = create_app()