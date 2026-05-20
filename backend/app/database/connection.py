import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

if os.getenv("USE_SQLITE", "").lower() in ("1", "true", "yes"):
    DATABASE_URL = os.getenv("SQLITE_URL", "sqlite:///./email_agent.db")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
else:
    DATABASE_URL = os.getenv(
        "DB_URL", "mysql+pymysql://root:password@localhost:3306/email_agent_db"
    )
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
