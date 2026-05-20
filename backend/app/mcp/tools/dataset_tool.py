import json

from langchain_core.tools import tool

from app.database.connection import SessionLocal
from app.services import dataset_service


@tool
def read_dataset_tool(dataset_id: int) -> str:
    """Read all contacts from a dataset by dataset_id. Returns name and email for each contact."""
    db = SessionLocal()
    try:
        dataset = dataset_service.get_dataset_by_id(db, dataset_id)
        if not dataset:
            return f"Dataset {dataset_id} not found."
        contacts = dataset_service.get_contacts_by_dataset(db, dataset_id)
        data = [
            {"name": c.name, "email": c.email, "company": c.company}
            for c in contacts
        ]
        return json.dumps({"dataset": dataset.name, "contacts": data}, indent=2)
    finally:
        db.close()


@tool
def list_datasets_tool() -> str:
    """List all datasets (id, name, contact count). Use when the user did not specify which dataset to use."""
    db = SessionLocal()
    try:
        datasets = dataset_service.list_datasets(db)
        result = []
        for d in datasets:
            count = len(dataset_service.get_contacts_by_dataset(db, d.id))
            result.append({"id": d.id, "name": d.name, "file_name": d.file_name, "contact_count": count})
        return json.dumps(result, indent=2)
    finally:
        db.close()
