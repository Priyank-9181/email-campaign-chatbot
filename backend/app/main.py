from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import campaigns, chat, datasets, stats
from app.database.connection import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Email Marketing Agent",
    description="LangChain + MCP + OpenRouter email marketing prototype",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173",
    "https://email-campaign-chatbot.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(campaigns.router)
app.include_router(chat.router)
app.include_router(stats.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
