from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("Contact", back_populates="dataset", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="dataset", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)

    dataset = relationship("Dataset", back_populates="contacts")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    email_body = Column(Text, nullable=False)
    status = Column(
        SQLEnum("draft", "sent", "failed", name="campaign_status", native_enum=False),
        default="draft",
    )
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="campaigns")
    send_logs = relationship("EmailSendLog", back_populates="campaign", cascade="all, delete-orphan")


class EmailSendLog(Base):
    __tablename__ = "email_send_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    status = Column(
        SQLEnum("success", "failed", name="send_status", native_enum=False),
        nullable=False,
    )
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="send_logs")


class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
