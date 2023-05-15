from fastapi import FastAPI
from src.api import router as api_router

app = FastAPI(title="ShopperCMS API")

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8080)
