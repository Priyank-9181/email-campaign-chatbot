from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services import dataset_service

router = APIRouter(prefix="/api", tags=["datasets"])


@router.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(None),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    content = await file.read()
    dataset_name = name or file.filename.replace(".csv", "")
    try:
        dataset = dataset_service.upload_csv_dataset(
            db, name=dataset_name, file_name=file.filename, file_bytes=content
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    contacts = dataset_service.get_contacts_by_dataset(db, dataset.id)
    return {
        "id": dataset.id,
        "name": dataset.name,
        "file_name": dataset.file_name,
        "contact_count": len(contacts),
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
    }


@router.get("/datasets")
def get_datasets(db: Session = Depends(get_db)):
    datasets = dataset_service.list_datasets(db)
    result = []
    for d in datasets:
        contacts = dataset_service.get_contacts_by_dataset(db, d.id)
        result.append(
            {
                "id": d.id,
                "name": d.name,
                "file_name": d.file_name,
                "contact_count": len(contacts),
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
        )
    return result


@router.get("/datasets/{dataset_id}/contacts")
def get_contacts(dataset_id: int, db: Session = Depends(get_db)):
    dataset = dataset_service.get_dataset_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    contacts = dataset_service.get_contacts_by_dataset(db, dataset_id)
    return [
        {"id": c.id, "name": c.name, "email": c.email, "company": c.company}
        for c in contacts
    ]


@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    if not dataset_service.delete_dataset(db, dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"message": "Dataset deleted"}
