from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.database import models
from app.services.dataset_service import get_contacts_by_dataset
from app.services.email_service import send_email


def list_campaigns(db: Session):
    return db.query(models.Campaign).order_by(models.Campaign.created_at.desc()).all()


def get_campaign_by_id(db: Session, campaign_id: int) -> Optional[models.Campaign]:
    return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()


def create_campaign(
    db: Session,
    campaign_name: str,
    subject: str,
    email_body: str,
    dataset_id: int,
    status: str = "draft",
) -> models.Campaign:
    campaign = models.Campaign(
        campaign_name=campaign_name,
        subject=subject,
        email_body=email_body,
        dataset_id=dataset_id,
        status=status,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def delete_campaign(db: Session, campaign_id: int) -> bool:
    campaign = get_campaign_by_id(db, campaign_id)
    if not campaign:
        return False
    db.delete(campaign)
    db.commit()
    return True


def get_send_logs(db: Session, campaign_id: int):
    return (
        db.query(models.EmailSendLog)
        .filter(models.EmailSendLog.campaign_id == campaign_id)
        .order_by(models.EmailSendLog.sent_at.desc())
        .all()
    )


def send_campaign_emails(db: Session, campaign_id: int) -> dict:
    campaign = get_campaign_by_id(db, campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}

    contacts = get_contacts_by_dataset(db, campaign.dataset_id)
    success, failed = 0, 0
    first_error: str | None = None

    for contact in contacts:
        try:
            send_email(
                to_email=contact.email,
                to_name=contact.name,
                subject=campaign.subject,
                body=campaign.email_body,
                company=contact.company,
            )
            log = models.EmailSendLog(
                campaign_id=campaign_id,
                recipient_email=contact.email,
                status="success",
            )
            success += 1
        except Exception as e:
            err = str(e)
            if first_error is None:
                first_error = err
            log = models.EmailSendLog(
                campaign_id=campaign_id,
                recipient_email=contact.email,
                status="failed",
                error_message=err,
            )
            failed += 1
        db.add(log)

    campaign.status = "sent" if failed == 0 else ("failed" if success == 0 else "sent")
    campaign.sent_at = datetime.utcnow()
    db.commit()

    out: dict = {"success": success, "failed": failed, "message": f"Success: {success} | Failed: {failed}"}
    if success == 0 and failed > 0 and first_error:
        low = first_error.lower()
        if "535" in first_error or "badcredentials" in low or "username and password not accepted" in low:
            out["hint"] = (
                "Gmail rejected SMTP login. Use an App Password (Google Account → Security → "
                "2-Step Verification → App passwords), not your normal Gmail password. Set SMTP_USER to your full "
                "Gmail address and SMTP_PASSWORD to the 16-character app password in backend/.env."
            )
    return out
