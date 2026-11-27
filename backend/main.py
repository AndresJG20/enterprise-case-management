from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routes import router

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title="CaseFlow", version="0.2.0", lifespan=lifespan)
app.include_router(router)

@app.get("/health")
def health():
    return {"status":"ok"}

app.mount("/", StaticFiles(directory=Path(__file__).resolve().parents[1]/"frontend", html=True), name="frontend")
