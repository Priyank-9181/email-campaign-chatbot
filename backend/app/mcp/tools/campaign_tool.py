import json

from langchain_core.tools import tool

from app.database.connection import SessionLocal
from app.services import campaign_service


@tool
def create_campaign_tool(
    campaign_name: str,
    subject: str,
    email_body: str,
    dataset_id: int,
) -> str:
    """Create a draft campaign in the database. dataset_id must be chosen by the user (or match their named dataset); never guess."""
    db = SessionLocal()
    try:
        campaign = campaign_service.create_campaign(
            db,
            campaign_name=campaign_name,
            subject=subject,
            email_body=email_body,
            dataset_id=dataset_id,
        )
        return f"Campaign created with id={campaign.id}, name='{campaign.campaign_name}'"
    finally:
        db.close()


@tool
def get_campaigns_tool() -> str:
    """List all campaigns with id, name, subject, status, and dataset_id."""
    db = SessionLocal()
    try:
        campaigns = campaign_service.list_campaigns(db)
        result = [
            {
                "id": c.id,
                "campaign_name": c.campaign_name,
                "subject": c.subject,
                "status": c.status,
                "dataset_id": c.dataset_id,
            }
            for c in campaigns
        ]
        return json.dumps(result, indent=2)
    finally:
        db.close()
