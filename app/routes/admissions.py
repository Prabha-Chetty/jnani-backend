import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pymongo.database import Database

from app.db.database import get_database
from app.schemas.admission import Admission, AdmissionCreate, AdmissionUpdate
from app.services import admission_service
from app.services.auth import get_current_user

router = APIRouter()


def admission_from_json(admission_json: str = Form(...)) -> AdmissionCreate:
    try:
        data = json.loads(admission_json)
        return AdmissionCreate(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in admission_json")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Admission validation failed: {e}")


@router.post("/", response_model=dict)
async def create_admission(
    admission: AdmissionCreate = Depends(admission_from_json),
    photo: Optional[UploadFile] = File(None),
    student_signature: Optional[str] = Form(None),
    parent_signature: Optional[str] = Form(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Submit a new admission. Signatures arrive as base64 data URLs."""
    result = admission_service.create_admission(
        db, admission, photo, student_signature, parent_signature
    )
    return {"message": "Admission submitted", **result}


@router.get("/", response_model=List[dict])
async def list_admissions(
    status: Optional[str] = None,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    return admission_service.list_admissions(db, status=status)


@router.get("/{admission_id}", response_model=dict)
async def get_admission(
    admission_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    doc = admission_service.get_admission(db, admission_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Admission not found")
    return doc


@router.put("/{admission_id}", response_model=dict)
async def update_admission(
    admission_id: str,
    update: AdmissionUpdate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    if not admission_service.update_admission(db, admission_id, update):
        raise HTTPException(status_code=404, detail="Admission not found or no changes")
    return {"message": "Admission updated"}


@router.patch("/{admission_id}/approve", response_model=dict)
async def approve_admission(
    admission_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    result = admission_service.approve_admission(db, admission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Admission not found")
    return result


@router.patch("/{admission_id}/reject", response_model=dict)
async def reject_admission(
    admission_id: str,
    reason: Optional[str] = None,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    if not admission_service.reject_admission(db, admission_id, reason):
        raise HTTPException(status_code=404, detail="Admission not found")
    return {"message": "Admission rejected"}


@router.delete("/{admission_id}", response_model=dict)
async def delete_admission(
    admission_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    if not admission_service.delete_admission(db, admission_id):
        raise HTTPException(status_code=404, detail="Admission not found")
    return {"message": "Admission deleted"}
