from pymongo.database import Database
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException

from app.schemas.student_attendance import StudentAttendanceBulk


def _day_from_date(date_str: str) -> str:
    """Derive the weekday name (e.g. 'Monday') from a YYYY-MM-DD string."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid date. Expected format YYYY-MM-DD.",
        )


def _date_query(month: Optional[int], year: Optional[int]):
    """Build a date prefix regex for the given month/year (dates stored as YYYY-MM-DD)."""
    if year and month:
        return {"$regex": f"^{year:04d}-{month:02d}"}
    if year:
        return {"$regex": f"^{year:04d}-"}
    return None


def save_bulk(db: Database, data: StudentAttendanceBulk, marked_by: Optional[str]) -> int:
    """Persist a day's roster into a single per-day document.

    Storage is one document per day: {date, day, present: [...], absent: [...]}.
    Each submitted student is *moved* to the right bucket (removed from the
    opposite one first), so a student is always in exactly one array and
    students not in this payload keep their previous status.
    """
    day = _day_from_date(data.date)

    present_ids = [e.student_id for e in data.entries if e.status == "present"]
    absent_ids = [e.student_id for e in data.entries if e.status == "absent"]
    all_ids = present_ids + absent_ids
    if not all_ids:
        return 0

    # Step 1: ensure the day document exists and pull the submitted ids out of
    # both buckets (so a status flip doesn't leave a student in both arrays).
    db.student_attendance.update_one(
        {"date": data.date, "student_id": {"$exists": False}},
        {
            "$setOnInsert": {"date": data.date, "day": day},
            "$set": {"marked_by": marked_by, "updated_at": datetime.utcnow().isoformat()},
            "$pull": {"present": {"$in": all_ids}, "absent": {"$in": all_ids}},
        },
        upsert=True,
    )

    # Step 2: add each submitted student to its bucket.
    add: dict = {}
    if present_ids:
        add["present"] = {"$each": present_ids}
    if absent_ids:
        add["absent"] = {"$each": absent_ids}
    if add:
        db.student_attendance.update_one(
            {"date": data.date, "student_id": {"$exists": False}},
            {"$addToSet": add},
        )

    return len(all_ids)


def list_attendance(
    db: Database,
    date: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
) -> List[dict]:
    """Flat, per-student view for a single day (date) or a month (month + year).

    Explodes the per-day documents back into one row per student so the roster
    and CSV keep their existing format.
    """
    query: dict = {"student_id": {"$exists": False}}
    if date:
        query["date"] = date
    else:
        date_q = _date_query(month, year)
        if date_q:
            query["date"] = date_q

    rows: List[dict] = []
    for doc in db.student_attendance.find(query).sort("date", 1):
        common = {
            "date": doc.get("date"),
            "day": doc.get("day"),
            "marked_by": doc.get("marked_by"),
        }
        for sid in doc.get("present", []) or []:
            rows.append({**common, "student_id": sid, "status": "present"})
        for sid in doc.get("absent", []) or []:
            rows.append({**common, "student_id": sid, "status": "absent"})
    return rows


def ensure_student_attendance_schema(db: Database) -> None:
    """Idempotent startup step: migrate any legacy per-student docs into per-day
    documents and enforce one document per day via a unique index on `date`."""
    legacy = list(db.student_attendance.find({"student_id": {"$exists": True}}))
    if legacy:
        buckets: dict = {}
        for doc in legacy:
            dt = doc.get("date")
            if not dt:
                continue
            b = buckets.setdefault(
                dt,
                {"day": doc.get("day"), "marked_by": doc.get("marked_by"),
                 "present": set(), "absent": set()},
            )
            sid = doc.get("student_id")
            if doc.get("status") == "present":
                b["present"].add(sid)
            elif doc.get("status") == "absent":
                b["absent"].add(sid)

        for dt, b in buckets.items():
            present = sorted(b["present"] - b["absent"])
            absent = sorted(b["absent"])
            add: dict = {}
            if present:
                add["present"] = {"$each": present}
            if absent:
                add["absent"] = {"$each": absent}
            update: dict = {
                "$setOnInsert": {"date": dt, "day": b["day"]},
                "$set": {"marked_by": b["marked_by"]},
            }
            if add:
                update["$addToSet"] = add
            db.student_attendance.update_one(
                {"date": dt, "student_id": {"$exists": False}}, update, upsert=True
            )

        db.student_attendance.delete_many({"student_id": {"$exists": True}})
        print(f"Migrated {len(legacy)} legacy student-attendance record(s) to per-day docs.")

    db.student_attendance.create_index("date", unique=True)
