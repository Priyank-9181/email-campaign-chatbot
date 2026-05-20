import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agent.langchain_agent import get_agent
from app.database.connection import get_db
from app.database import models
from app.services.clarification_service import (
    build_clarification,
    format_clarification_response,
    parse_stored_response,
    serialize_stored_response,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    prompt: str
    skip_clarification: bool = False


def _prior_messages_for_agent(db: Session, max_turns: int):
    """Build LangChain message list from stored Q/A pairs (oldest first)."""
    rows = (
        db.query(models.AIChatHistory)
        .order_by(models.AIChatHistory.created_at.desc())
        .limit(max_turns)
        .all()
    )
    rows = list(reversed(rows))
    messages = []
    for r in rows:
        text, _ = parse_stored_response(r.response)
        messages.append(HumanMessage(content=r.prompt))
        messages.append(AIMessage(content=text))
    return messages


@router.post("/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    max_turns = int(os.getenv("CHAT_HISTORY_MAX_TURNS", "15"))
    chat_history = _prior_messages_for_agent(db, max_turns=max_turns)

    clarification = build_clarification(
        payload.prompt,
        db,
        chat_history=chat_history,
        skip_clarification=payload.skip_clarification,
    )

    if clarification:
        response_text = format_clarification_response(clarification)
        stored = serialize_stored_response(response_text, clarification)
        db.add(models.AIChatHistory(prompt=payload.prompt, response=stored))
        db.commit()
        return {
            "prompt": payload.prompt,
            "response": response_text,
            "clarification": clarification,
        }

    agent = get_agent()
    try:
        result = agent.invoke({"input": payload.prompt, "chat_history": chat_history})
        response_text = result.get("output", str(result))
    except Exception as e:
        logger.exception("Agent invoke failed")
        msg = str(e)
        if "max execution time" in msg.lower() or "execution time" in msg.lower():
            detail = (
                "The agent stopped because it ran too long. Try a shorter request, "
                "or increase AGENT_MAX_EXECUTION_SEC in .env."
            )
        else:
            detail = f"Agent error: {msg}"
        raise HTTPException(status_code=502, detail=detail) from e

    db.add(
        models.AIChatHistory(
            prompt=payload.prompt,
            response=serialize_stored_response(response_text, None),
        )
    )
    db.commit()

    return {"prompt": payload.prompt, "response": response_text, "clarification": None}


@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db)):
    rows = (
        db.query(models.AIChatHistory)
        .order_by(models.AIChatHistory.created_at.desc())
        .limit(50)
        .all()
    )
    result = []
    for r in reversed(rows):
        text, clarification = parse_stored_response(r.response)
        item = {
            "id": r.id,
            "prompt": r.prompt,
            "response": text,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        if clarification:
            item["clarification"] = clarification
        result.append(item)
    return result
