import io
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.database import models


def list_datasets(db: Session):
    return db.query(models.Dataset).order_by(models.Dataset.created_at.desc()).all()


def get_dataset_by_id(db: Session, dataset_id: int) -> Optional[models.Dataset]:
    return db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()


def get_contacts_by_dataset(db: Session, dataset_id: int):
    return db.query(models.Contact).filter(models.Contact.dataset_id == dataset_id).all()


def delete_dataset(db: Session, dataset_id: int) -> bool:
    dataset = get_dataset_by_id(db, dataset_id)
    if not dataset:
        return False
    db.delete(dataset)
    db.commit()
    return True


def upload_csv_dataset(db: Session, name: str, file_name: str, file_bytes: bytes) -> models.Dataset:
    df = pd.read_csv(io.BytesIO(file_bytes))
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "email" not in df.columns:
        raise ValueError("CSV must contain an 'email' column")

    name_col = "name" if "name" in df.columns else df.columns[0]
    company_col = "company" if "company" in df.columns else None

    dataset = models.Dataset(name=name, file_name=file_name)
    db.add(dataset)
    db.flush()

    for _, row in df.iterrows():
        email = str(row["email"]).strip()
        if not email or email == "nan":
            continue
        contact = models.Contact(
            dataset_id=dataset.id,
            name=str(row.get(name_col, "")).strip() if name_col in df.columns else "",
            email=email,
            company=str(row[company_col]).strip() if company_col and pd.notna(row.get(company_col)) else None,
        )
        db.add(contact)

    db.commit()
    db.refresh(dataset)
    return dataset
