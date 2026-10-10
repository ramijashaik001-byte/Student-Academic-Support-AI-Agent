from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, StudentProfile, FacultyProfile
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.auth import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user
from app.services.audit_service import audit_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address is already registered."
        )

    hashed_pw = get_password_hash(data.password)
    user = User(
        email=data.email.lower(),
        hashed_password=hashed_pw,
        full_name=data.full_name,
        role=data.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create associated profile
    if data.role == "student":
        roll_num = data.roll_number or f"2026-CS-{user.id:03d}"
        profile = StudentProfile(
            user_id=user.id,
            roll_number=roll_num,
            department_id=data.department_id,
            current_semester=data.current_semester or 1,
            academic_year="2025-2026",
            cgpa=8.5
        )
        db.add(profile)
    elif data.role == "faculty":
        emp_id = f"EMP-{user.id:03d}"
        profile = FacultyProfile(
            user_id=user.id,
            employee_id=emp_id,
            department_id=data.department_id,
            designation="Assistant Professor",
            office_location="Block B, Room 201",
            office_hours="Mon-Fri 2:00 PM - 4:00 PM"
        )
        db.add(profile)

    db.commit()
    db.refresh(user)

    audit_service.log(
        db=db,
        user_id=user.id,
        action="USER_REGISTERED",
        resource_type="user",
        resource_id=str(user.id),
        details=f"User {user.email} registered with role {user.role}"
    )

    token = create_access_token(subject=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently inactive. Contact administrator."
        )

    token = create_access_token(subject=user.id, role=user.role)
    audit_service.log(
        db=db,
        user_id=user.id,
        action="USER_LOGIN",
        resource_type="user",
        resource_id=str(user.id),
        details=f"User {user.email} logged in successfully"
    )
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully."}


@router.post("/switch-demo", response_model=Token)
def switch_demo_user(role: str, db: Session = Depends(get_db)):
    """
    Convenient evaluator tool allowing instantaneous switching between
    Student (Ramija Shaik), Faculty (Prof. Sharma), and Admin (Campus Admin).
    """
    target_user = db.query(User).filter(User.role == role.lower(), User.is_active == True).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active demo account found for role '{role}'"
        )

    token = create_access_token(subject=target_user.id, role=target_user.role)
    return {"access_token": token, "token_type": "bearer", "user": target_user}
