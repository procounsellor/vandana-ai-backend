from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import GOOGLE_CLIENT_ID
from app.db import engine
from app.routes import chat, avatar, auth, conversations

app = FastAPI(title="Vandana AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(avatar.router)
app.include_router(conversations.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/demo", response_class=HTMLResponse)
def demo():
    with open("static/index.html", "r") as f:
        html = f.read()
    client_id = GOOGLE_CLIENT_ID or ""
    html = html.replace("</head>", f'<script>window.__GOOGLE_CLIENT_ID__ = "{client_id}";</script>\n</head>', 1)
    return HTMLResponse(html)


@app.get("/")
def root():
    return {"message": "Vandana AI backend is running"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        value = result.scalar()
    return {"db_connected": value == 1}