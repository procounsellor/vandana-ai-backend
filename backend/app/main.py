from fastapi import FastAPI
from sqlalchemy import text
from app.db import engine

app = FastAPI(title="Vandana AI Backend")


@app.get("/")
def root():
    return {"message": "Vandana AI backend is running"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        value = result.scalar()
    return {"db_connected": value == 1}