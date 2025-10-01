from fastapi import FastAPI
from app.db.session import init_db
from app.api.endpoints import crops, seasons

app = FastAPI(title="Mshamba Intelligence API")

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(crops.router, prefix="/crops", tags=["crops"])
app.include_router(seasons.router, prefix="/seasons", tags=["seasons"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Mshamba Intelligence API"}