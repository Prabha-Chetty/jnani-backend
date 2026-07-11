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


def _amount_for_minutes(minutes: int, rate: float, class_minutes: int) -> float:
    """Amount payable for the minutes taught, by whole completed classes.

    A class is `class_minutes` long and pays `rate`. Only fully completed
    classes are paid; e.g. with 45 min / Rs.250 a 90-minute session pays
    Rs.500 and a 60-minute session pays Rs.250.
    """
    classes = (minutes or 0) // (class_minutes or 1)
    return round(classes * rate, 2)


def _faculty_doc(db: Database, faculty_id: str, cache: dict) -> Optional[dict]:
    """Fetch (and cache for the request) a faculty document by id."""
    if faculty_id in cache:
        return cache[faculty_id]
    doc = None
    try:
        doc = db.faculties.find_one({"_id": ObjectId(faculty_id)})
    except (InvalidId, TypeError):
        doc = None
    cache[faculty_id] = doc
    return doc


def _faculty_name(db: Database, faculty_id: str, cache: dict) -> Optional[str]:
    doc = _faculty_doc(db, faculty_id, cache)
    return doc.get("name") if doc else None


def _effective_rate(db: Database, faculty_id: str, cache: dict) -> tuple:
    """(rate_per_class, class_minutes) for a faculty.

    Uses the faculty's per-faculty overrides when set, otherwise the global
    defaults from settings.
    """
    doc = _faculty_doc(db, faculty_id, cache) or {}
    rate = doc.get("rate_per_class")
    cm = doc.get("class_minutes")
    return (
        rate if rate is not None else settings.RATE_PER_CLASS,
        cm if cm is not None else settings.CLASS_MINUTES,
    )


def _serialize(db: Database, doc: dict, cache: dict) -> dict:
    doc["id"] = str(doc["_id"])
    doc["faculty_name"] = _faculty_name(db, doc.get("faculty_id"), cache)
    # Amount is frozen at save time (Option B). Prefer the stored snapshot;
    # fall back to the faculty's effective rate for legacy rows saved before
    # per-entry rates existed.
    rate = doc.get("rate_per_class")
    cm = doc.get("class_minutes")
    if rate is None or cm is None:
        rate, cm = _effective_rate(db, doc.get("faculty_id"), cache)
    doc["rate_per_class"] = rate
    doc["class_minutes"] = cm
    if doc.get("amount") is None:
        doc["amount"] = _amount_for_minutes(doc.get("minutes_taken", 0), rate, cm)
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

    # Freeze the faculty's rate onto the entry so later rate changes don't
    # re-price this record (Option B).
    rate, cm = _effective_rate(db, faculty_id, {})

    doc = {
        "faculty_id": faculty_id,
        "date": data.date,
        "day": day,
        "minutes_taken": data.minutes_taken,
        "notes": data.notes,
        "rate_per_class": rate,
        "class_minutes": cm,
        "amount": _amount_for_minutes(data.minutes_taken, rate, cm),
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
    # Per-faculty rates mean the amount can't be a single constant in a Mongo
    # aggregation, so totals are rolled up in Python from each entry's frozen
    # amount (fallback-computed for legacy rows). This keeps the summary in
    # exact agreement with the per-day amounts on the calendar.
    query: dict = {}
    date_q = _date_query(month, year)
    if date_q:
        query["date"] = date_q

    docs = list(db.attendance.find(query))
    cache: dict = {}
    agg: dict = {}
    for d in docs:
        fid = d.get("faculty_id")
        rate = d.get("rate_per_class")
        cm = d.get("class_minutes")
        if rate is None or cm is None:
            rate, cm = _effective_rate(db, fid, cache)
        amount = d.get("amount")
        if amount is None:
            amount = _amount_for_minutes(d.get("minutes_taken", 0), rate, cm)
        row = agg.setdefault(
            fid, {"total_minutes": 0, "total_amount": 0.0, "days": 0}
        )
        row["total_minutes"] += int(d.get("minutes_taken", 0) or 0)
        row["total_amount"] += amount
        row["days"] += 1

    result = [
        {
            "faculty_id": fid,
            "faculty_name": _faculty_name(db, fid, cache),
            "total_minutes": row["total_minutes"],
            "total_amount": round(row["total_amount"], 2),
            "days": row["days"],
        }
        for fid, row in agg.items()
    ]
    result.sort(key=lambda x: (x["faculty_name"] or "").lower())
    return result


def update_attendance(db: Database, attendance_id: str, data: AttendanceUpdate) -> bool:
    oid = _to_object_id(attendance_id)
    existing = db.attendance.find_one({"_id": oid})
    if not existing:
        return False

    update = data.dict(exclude_unset=True)
    if update.get("date"):
        update["day"] = _day_from_date(update["date"])

    # Keep the entry's frozen rate stable across edits. Backfill it for legacy
    # rows that predate per-entry rates, then re-derive the frozen amount from
    # the (possibly updated) minutes at that rate.
    rate = existing.get("rate_per_class")
    cm = existing.get("class_minutes")
    if rate is None or cm is None:
        rate, cm = _effective_rate(db, existing.get("faculty_id"), {})
        update["rate_per_class"] = rate
        update["class_minutes"] = cm
    minutes = update.get("minutes_taken", existing.get("minutes_taken", 0))
    update["amount"] = _amount_for_minutes(minutes, rate, cm)

    result = db.attendance.update_one({"_id": oid}, {"$set": update})
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
