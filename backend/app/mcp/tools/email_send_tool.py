from langchain_core.tools import tool

from app.database.connection import SessionLocal
from app.services import campaign_service


@tool
def send_email_campaign_tool(campaign_id: int) -> str:
    """
    Sends real emails to every contact in the campaign's dataset. Use ONLY when the user
    explicitly asked to send/deliver/dispatch/blast/mail the campaign. Never use for
    "create" or "draft" only. Input: campaign_id (integer).
    """
    db = SessionLocal()
    try:
        result = campaign_service.send_campaign_emails(db, campaign_id)
        if "error" in result:
            return result["error"]
        return f"Campaign sent. Success: {result['success']} | Failed: {result['failed']}"
    finally:
        db.close()
