from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import AdminLogin
from app.schemas.token import Token
from app.services.auth import create_access_token, authenticate_user
from app.db.database import get_database
from pymongo.database import Database
from datetime import timedelta

router = APIRouter()

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