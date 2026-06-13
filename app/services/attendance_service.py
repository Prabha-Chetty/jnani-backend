from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from typing import Optional
from fastapi import HTTPException

from app.config import settings
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


def _day_from_date(date_str: str) -> str:
    """Derive the weekday name (e.g. 'Monday') from a YYYY-MM-DD string."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid date. Expected format YYYY-MM-DD.",
        )


def _to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail="Invalid id.")


def _amount_for_day() -> float:
    """Flat amount payable for a day attended, regardless of minutes taught."""
    return round(settings.RATE_PER_DAY, 2)


def _faculty_name(db: Database, faculty_id: str, cache: dict) -> Optional[str]:
    if faculty_id in cache:
        return cache[faculty_id]
    name = None
    try:
        faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
        if faculty:
            name = faculty.get("name")
    except (InvalidId, TypeError):
        name = None
    cache[faculty_id] = name
    return name


def _serialize(db: Database, doc: dict, cache: dict) -> dict:
    doc["id"] = str(doc["_id"])
    doc["faculty_name"] = _faculty_name(db, doc.get("faculty_id"), cache)
    doc["amount"] = _amount_for_day()
    return doc


def _date_query(month: Optional[int], year: Optional[int]):
    """Build a date prefix regex for the given month/year (dates stored as YYYY-MM-DD)."""
    if year and month:
        return {"$regex": f"^{year:04d}-{month:02d}"}
    if year:
        return {"$regex": f"^{year:04d}-"}
    return None


def create_attendance(
    db: Database, faculty_id: str, data: AttendanceCreate, marked_by: Optional[str]
) -> str:
    day = _day_from_date(data.date)

    # One entry per faculty per day.
    if db.attendance.find_one({"faculty_id": faculty_id, "date": data.date}):
        raise HTTPException(
            status_code=400,
            detail="Attendance for this date is already recorded.",
        )

    doc = {
        "faculty_id": faculty_id,
        "date": data.date,
        "day": day,
        "minutes_taken": data.minutes_taken,
        "notes": data.notes,
        "marked_by": marked_by,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = db.attendance.insert_one(doc)
    return str(result.inserted_id)


def list_attendance(
    db: Database,
    faculty_id: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
):
    query: dict = {}
    if faculty_id:
        query["faculty_id"] = faculty_id
    date_q = _date_query(month, year)
    if date_q:
        query["date"] = date_q

    docs = list(db.attendance.find(query).sort("date", 1))
    cache: dict = {}
    return [_serialize(db, d, cache) for d in docs]


def summary(db: Database, month: Optional[int] = None, year: Optional[int] = None):
    pipeline = []
    date_q = _date_query(month, year)
    if date_q:
        pipeline.append({"$match": {"date": date_q}})
    pipeline.append(
        {
            "$group": {
                "_id": "$faculty_id",
                "total_minutes": {"$sum": "$minutes_taken"},
                "days": {"$sum": 1},
            }
        }
    )

    rows = list(db.attendance.aggregate(pipeline))
    cache: dict = {}
    result = []
    for r in rows:
        fid = r["_id"]
        days = r.get("days", 0)
        # Flat amount per day attended.
        result.append(
            {
                "faculty_id": fid,
                "faculty_name": _faculty_name(db, fid, cache),
                "total_minutes": int(r.get("total_minutes", 0)),
                "total_amount": round(days * settings.RATE_PER_DAY, 2),
                "days": days,
            }
        )
    result.sort(key=lambda x: (x["faculty_name"] or "").lower())
    return result


def update_attendance(db: Database, attendance_id: str, data: AttendanceUpdate) -> bool:
    update = data.dict(exclude_unset=True)
    if update.get("date"):
        update["day"] = _day_from_date(update["date"])
    if not update:
        return False
    result = db.attendance.update_one(
        {"_id": _to_object_id(attendance_id)}, {"$set": update}
    )
    return result.matched_count > 0


def delete_attendance(db: Database, attendance_id: str) -> bool:
    result = db.attendance.delete_one({"_id": _to_object_id(attendance_id)})
    return result.deleted_count > 0


def purge_legacy_hours_records(db: Database) -> int:
    """One-time cleanup: remove old attendance entries stored as `hours_taken`.

    The schema moved from hours to whole-minute tracking; legacy records are
    ambiguous, so they are wiped. Idempotent — new minute-based docs have no
    `hours_taken` field and are never matched.
    """
    result = db.attendance.delete_many({"hours_taken": {"$exists": True}})
    return result.deleted_count
