import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    body: str,
    company: Optional[str] = None,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{os.getenv('SENDER_NAME', 'AI Email Agent')} <{os.getenv('SMTP_USER')}>"
    msg["To"] = to_email

    personalized_body = body.replace("{{name}}", to_name or "there")
    personalized_body = personalized_body.replace("{{email}}", to_email or "")
    personalized_body = personalized_body.replace("{{company}}", company or "")

    b = personalized_body.strip()
    looks_html = "<html" in b.lower() or "<body" in b.lower() or "<div" in b.lower() or "<p" in b.lower() or "<table" in b.lower() or "<br" in b.lower() or "<a " in b.lower()
    subtype = "html" if looks_html else "plain"

    msg.attach(MIMEText(personalized_body, subtype))

    with smtplib.SMTP(os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", 587))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.sendmail(os.getenv("SMTP_USER"), to_email, msg.as_string())
