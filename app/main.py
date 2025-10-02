from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import init_db
from app.api.endpoints import crops, seasons

app = FastAPI(title="Mshamba Intelligence API")

origins = [
    "http://umunu-kh777-77774-qaaca-cai.localhost:4943", # Your frontend's origin
    "http://localhost:4943", # Potentially another local frontend origin
    "http://127.0.0.1:4943", # Another common local frontend origin
    # You might need to add other origins if your frontend runs on different ports or domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(crops.router, prefix="/crops", tags=["crops"])
app.include_router(seasons.router, prefix="/seasons", tags=["seasons"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Mshamba Intelligence API"}