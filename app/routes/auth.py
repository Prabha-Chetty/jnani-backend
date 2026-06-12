from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import AdminLogin
from app.schemas.token import Token
from app.services.auth import create_access_token, authenticate_user, get_current_user, is_admin
from app.db.database import get_database
from pymongo.database import Database
from datetime import timedelta
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter()


@router.get("/me")
async def read_current_user(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """Return the profile of the logged-in user, including their linked
    faculty (if any) and admin flag. Used by the frontend for role-gating."""
    faculty_id = current_user.get("faculty_id")
    faculty_name = None
    if faculty_id:
        try:
            faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
            if faculty:
                faculty_name = faculty.get("name")
        except (InvalidId, TypeError):
            faculty_name = None

    return {
        "id": str(current_user["_id"]),
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "roles": current_user.get("roles", []),
        "faculty_id": faculty_id,
        "faculty_name": faculty_name,
        "is_admin": is_admin(current_user),
    }

@router.post("/login", response_model=Token)
async def login_for_access_token(
    admin_data: AdminLogin,
    db: Database = Depends(get_database)
):
    user = authenticate_user(db, admin_data.email, admin_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Refresh the access token for the current user"""
    # Verify the user still exists in the database
    user = db.users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create a new access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 