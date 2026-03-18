from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db import engine
from app.routes import chat, avatar

app = FastAPI(title="Vandana AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(avatar.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/demo")
def demo():
    return FileResponse("static/index.html")


@app.get("/")
def root():
    return {"message": "Vandana AI backend is running"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        value = result.scalar()
    return {"db_connected": value == 1}