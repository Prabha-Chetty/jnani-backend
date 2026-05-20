from datetime import datetime, date
from typing import List, Optional

from bson import ObjectId
from fastapi import UploadFile
from pymongo.database import Database

from app.schemas.admission import AdmissionCreate, AdmissionUpdate
from app.services import cloudinary_service


def _generate_reference_no(db: Database) -> str:
    """JSC-YYYY-NNNN where NNNN auto-increments per calendar year."""
    year = datetime.utcnow().year
    prefix = f"JSC-{year}-"
    last = db.admissions.find_one(
        {"reference_no": {"$regex": f"^{prefix}"}},
        sort=[("reference_no", -1)],
    )
    next_num = 1
    if last and last.get("reference_no"):
        try:
            next_num = int(last["reference_no"].split("-")[-1]) + 1
        except (ValueError, IndexError):
            next_num = 1
    return f"{prefix}{next_num:04d}"


def _serialise(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if isinstance(doc.get("dob"), datetime):
        doc["dob"] = doc["dob"].date().isoformat()
    elif isinstance(doc.get("dob"), date):
        doc["dob"] = doc["dob"].isoformat()
    for key in ("submitted_at", "approved_at", "rejected_at"):
        val = doc.get(key)
        if isinstance(val, datetime):
            doc[key] = val.isoformat()
    return doc


def create_admission(
    db: Database,
    admission: AdmissionCreate,
    photo: Optional[UploadFile],
    student_signature_data_url: Optional[str],
    parent_signature_data_url: Optional[str],
) -> dict:
    data = admission.model_dump()
    # Pydantic gives us date objects; Mongo wants datetime for sort/index support.
    if isinstance(data.get("dob"), date):
        data["dob"] = datetime.combine(data["dob"], datetime.min.time())

    data["reference_no"] = _generate_reference_no(db)
    data["status"] = "pending"
    data["submitted_at"] = datetime.utcnow()
    data["photo_url"] = None
    data["student_signature_url"] = None
    data["parent_signature_url"] = None

    if photo:
        uploaded = cloudinary_service.upload_file(photo, folder="admissions/photos")
        data["photo_url"] = uploaded["url"]
        data["photo_public_id"] = uploaded["public_id"]

    if student_signature_data_url:
        uploaded = cloudinary_service.upload_data_url(
            student_signature_data_url, folder="admissions/signatures"
        )
        data["student_signature_url"] = uploaded["url"]
        data["student_signature_public_id"] = uploaded["public_id"]

    if parent_signature_data_url:
        uploaded = cloudinary_service.upload_data_url(
            parent_signature_data_url, folder="admissions/signatures"
        )
        data["parent_signature_url"] = uploaded["url"]
        data["parent_signature_public_id"] = uploaded["public_id"]

    result = db.admissions.insert_one(data)
    return {"id": str(result.inserted_id), "reference_no": data["reference_no"]}


def list_admissions(db: Database, status: Optional[str] = None) -> List[dict]:
    query = {}
    if status:
        query["status"] = status
    docs = list(db.admissions.find(query).sort("submitted_at", -1))
    return [_serialise(d) for d in docs]


def get_admission(db: Database, admission_id: str) -> Optional[dict]:
    doc = db.admissions.find_one({"_id": ObjectId(admission_id)})
    return _serialise(doc) if doc else None


def update_admission(db: Database, admission_id: str, update: AdmissionUpdate) -> bool:
    data = {k: v for k, v in update.model_dump(exclude_unset=True).items() if v is not None}
    if isinstance(data.get("dob"), date):
        data["dob"] = datetime.combine(data["dob"], datetime.min.time())
    if not data:
        return False
    result = db.admissions.update_one(
        {"_id": ObjectId(admission_id)}, {"$set": data}
    )
    return result.modified_count > 0


def approve_admission(db: Database, admission_id: str) -> Optional[dict]:
    """Approve admission and create a Student record from it."""
    admission = db.admissions.find_one({"_id": ObjectId(admission_id)})
    if not admission:
        return None
    if admission.get("status") == "approved":
        return _serialise(admission)

    student_doc = {
        "name": admission["student_name"],
        "class_name": admission.get("enrolling_class", ""),
        "parent_name": admission["parent_declaration_name"],
        "contact_number": admission["parent_phone"],
        "profile_image_url": admission.get("photo_url"),
        "joined_date": datetime.utcnow(),
        "admission_ref": admission["reference_no"],
    }
    student_result = db.students.insert_one(student_doc)

    db.admissions.update_one(
        {"_id": ObjectId(admission_id)},
        {
            "$set": {
                "status": "approved",
                "approved_at": datetime.utcnow(),
                "converted_student_id": str(student_result.inserted_id),
            }
        },
    )
    return _serialise(db.admissions.find_one({"_id": ObjectId(admission_id)}))


def reject_admission(db: Database, admission_id: str, reason: Optional[str] = None) -> bool:
    update = {"status": "rejected", "rejected_at": datetime.utcnow()}
    if reason:
        update["rejection_reason"] = reason
    result = db.admissions.update_one(
        {"_id": ObjectId(admission_id)}, {"$set": update}
    )
    return result.modified_count > 0


def delete_admission(db: Database, admission_id: str) -> bool:
    doc = db.admissions.find_one({"_id": ObjectId(admission_id)})
    if not doc:
        return False
    for key in ("photo_public_id", "student_signature_public_id", "parent_signature_public_id"):
        pid = doc.get(key)
        if pid:
            cloudinary_service.delete_by_public_id(pid)
    result = db.admissions.delete_one({"_id": ObjectId(admission_id)})
    return result.deleted_count > 0
