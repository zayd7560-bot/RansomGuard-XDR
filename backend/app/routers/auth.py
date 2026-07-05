from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from app.schemas import RegisterRequest, LoginRequest
from app.database import get_db
from app.models import User
from app.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.security import get_current_user
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "email": current_user.email,
        "role": "Administrator",
        "profile_image": current_user.profile_image
    }
@router.get("/test")
async def test():
    return {
        "message": "Authentication Router Working"
    }


@router.post("/register")
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    username_exists = db.query(User).filter(
        User.username == data.username
    ).first()

    if username_exists:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    email_exists = db.query(User).filter(
        User.email == data.email
    ).first()

    if email_exists:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
    full_name=data.full_name,
    username=data.username,
    email=data.email,
    password_hash=hash_password(data.password),
    duress_password_hash=hash_password(
        data.duress_password
    )
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User Registered Successfully",
        "id": new_user.id,
        "username": new_user.username
    }
@router.post("/login")
async def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token(
        {
            "username": user.username
        }
    )

    return {
        "access_token": token,
        "token_type": "Bearer",
        "username": user.username
    }
@router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    os.makedirs("uploads/profile", exist_ok=True)

    ext = os.path.splitext(file.filename)[1]

    filename = f"{uuid.uuid4()}{ext}"

    filepath = os.path.join(
        "uploads",
        "profile",
        filename
    )

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.profile_image = f"profile/{filename}"

    db.commit()

    return {
        "success": True,
        "image": current_user.profile_image
    }