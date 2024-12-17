from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    PasswordReset,
    VerifyEmail,
    PasswordResetConfirm,
    UserResponse,
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core import email
from app.core.settings import settings
import uuid
import random
import string
from datetime import datetime, timedelta
from app.core.logger import logger

router = APIRouter()

# Configuration constants
MAX_VERIFICATION_ATTEMPTS = 5  # Maximum verification attempts
VERIFICATION_CODE_COOLDOWN = 60  # Verification code cooldown time (seconds)
VERIFICATION_CODE_EXPIRE = 10  # Verification code expiration time (minutes)


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
):
    # check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # create user
    verification_code = str(uuid.uuid4())
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        verification_code=verification_code,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # send verification email
    verification_url = f"{settings.FRONTEND_URL}/verify-email?code={verification_code}"
    background_tasks.add_task(
        email.send_email,
        email_to=user.email,
        subject="Verify your email",
        template_name="verify_email",
        data={"verification_url": verification_url},
    )

    return db_user


@router.get("/verify-email/{code}")
async def verify_email(code: str, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.verification_code == code).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user.is_verified = True
    user.verification_code = None
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
):
    logger.info(f"Forgot password request: {request}")
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_code = generate_verification_code()
    user.reset_password_code = reset_code
    db.commit()

    # Send verification code email
    background_tasks.add_task(
        email.send_email,
        email_to=request.email,
        subject="Email verification code",
        template_name="verification_code",
        data={"verification_code": reset_code},
    )
    # reset_url = f"{settings.FRONTEND_URL}/reset-password?code={reset_code}"
    # background_tasks.add_task(
    #     email.send_email,
    #     email_to=user.email,
    #     subject="Reset password",
    #     template_name="reset_password",
    #     data={"reset_url": reset_url},
    # )
    logger.info(f"reset_url: {reset_code}")
    logger.info(f"Password reset email sent to {user.email}")

    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm, db: Session = Depends(deps.get_db)
):
    user = (
        db.query(User)
        .filter(User.email == request.email, User.reset_password_code == request.code)
        .first()
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    user.hashed_password = get_password_hash(request.new_password)
    user.reset_password_code = None
    db.commit()

    return {"message": "Password reset successfully"}


def generate_verification_code():
    """Generate a 6-digit verification code"""
    return "".join(random.choices(string.digits, k=6))


@router.post("/send-verification-code")
async def send_verification_code(
    email: str, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db)
):
    # Get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is already verified
    if user.is_active and user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    # Check if user has sent a verification code recently
    if user.last_verification_sent_at:
        cooldown_end = user.last_verification_sent_at + timedelta(
            seconds=VERIFICATION_CODE_COOLDOWN
        )
        if datetime.utcnow() < cooldown_end:
            seconds_left = int((cooldown_end - datetime.utcnow()).total_seconds())
            raise HTTPException(
                status_code=400,
                detail=f"Please wait {seconds_left} seconds before requesting a new code",
            )

    # Reset verification attempts and generate a new verification code
    verification_code = generate_verification_code()
    user.verification_code = verification_code
    user.verification_code_expires_at = datetime.utcnow() + timedelta(
        minutes=VERIFICATION_CODE_EXPIRE
    )
    user.verification_attempts = 0
    user.last_verification_sent_at = datetime.utcnow()
    db.commit()

    # Send verification code email
    background_tasks.add_task(
        email.send_email,
        email_to=email,
        subject="Email verification code",
        template_name="verification_code",
        data={"verification_code": verification_code},
    )

    return {
        "message": "Verification code sent",
        "expires_in": f"{VERIFICATION_CODE_EXPIRE} minutes",
    }


@router.post("/verify-email")
async def verify_email(verify_data: VerifyEmail, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == verify_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Basic verification code check
    if not user.verification_code or not user.verification_code_expires_at:
        raise HTTPException(status_code=400, detail="No verification code found")

    # Check if maximum attempts are exceeded
    if user.verification_attempts >= MAX_VERIFICATION_ATTEMPTS:
        # Clear verification code, force user to send again
        user.verification_code = None
        user.verification_code_expires_at = None
        user.verification_attempts = 0
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Maximum verification attempts exceeded. Please request a new code",
        )

    # Check if verification code is expired
    if datetime.utcnow() > user.verification_code_expires_at:
        raise HTTPException(status_code=400, detail="Verification code expired")

    # Verification code error handling
    if user.verification_code != verify_data.verification_code:
        user.verification_attempts += 1
        attempts_left = MAX_VERIFICATION_ATTEMPTS - user.verification_attempts
        db.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verification code. {attempts_left} attempts remaining",
        )

    # Verification successful, activate user and clear verification related information
    user.is_active = True
    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    user.verification_attempts = 0
    user.last_verification_sent_at = None
    db.commit()

    return {
        "message": "Email verified successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        },
    }
