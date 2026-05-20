from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services import campaign_service

router = APIRouter(prefix="/api", tags=["campaigns"])


class CampaignCreate(BaseModel):
    campaign_name: str
    subject: str
    email_body: str
    dataset_id: int


@router.post("/campaigns")
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    campaign = campaign_service.create_campaign(
        db,
        campaign_name=payload.campaign_name,
        subject=payload.subject,
        email_body=payload.email_body,
        dataset_id=payload.dataset_id,
    )
    return _campaign_to_dict(campaign)


@router.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = campaign_service.list_campaigns(db)
    return [_campaign_to_dict(c) for c in campaigns]


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign_by_id(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _campaign_to_dict(campaign)


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    if not campaign_service.delete_campaign(db, campaign_id):
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted"}


@router.post("/campaigns/{campaign_id}/send")
def send_campaign(campaign_id: int, db: Session = Depends(get_db)):
    result = campaign_service.send_campaign_emails(db, campaign_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/campaigns/{campaign_id}/logs")
def get_campaign_logs(campaign_id: int, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign_by_id(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    logs = campaign_service.get_send_logs(db, campaign_id)
    return [
        {
            "id": log.id,
            "recipient_email": log.recipient_email,
            "status": log.status,
            "error_message": log.error_message,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
        }
        for log in logs
    ]


def _campaign_to_dict(campaign):
    return {
        "id": campaign.id,
        "campaign_name": campaign.campaign_name,
        "subject": campaign.subject,
        "email_body": campaign.email_body,
        "status": campaign.status,
        "dataset_id": campaign.dataset_id,
        "sent_at": campaign.sent_at.isoformat() if campaign.sent_at else None,
        "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
    }
