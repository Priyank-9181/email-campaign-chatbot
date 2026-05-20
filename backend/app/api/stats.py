from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models
from app.database.connection import get_db
from app.services import campaign_service, dataset_service

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    datasets = dataset_service.list_datasets(db)
    campaigns = campaign_service.list_campaigns(db)
    sent_logs = (
        db.query(models.EmailSendLog)
        .filter(models.EmailSendLog.status == "success")
        .count()
    )
    return {
        "datasets": len(datasets),
        "campaigns": len(campaigns),
        "emails_sent": sent_logs,
        "recent_campaigns": [
            {
                "id": c.id,
                "campaign_name": c.campaign_name,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in campaigns[:5]
        ],
    }
