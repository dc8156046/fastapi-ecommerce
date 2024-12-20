from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_active_superuser, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get(
    "/", response_model=dict, summary="Get users list", status_code=status.HTTP_200_OK
)
async def get_users(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    users = db.query(User).offset(skip).limit(limit).all()
    return {
        "message": "Get users list successfully",
        "data": users,
        "total": len(users),
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/{user_id}",
    response_model=dict,
    summary="Get user detail",
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return {"message": "Get user detail successfully", "data": user}


@router.post(
    "/", response_model=dict, summary="Create user", status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    # Check if user with same email exists
    if db.query(User).filter(User.email == user_create.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    try:
        # Create new user
        user_data = user_create.model_dump()
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"message": "Create user successfully", "data": db_user}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{user_id}",
    response_model=dict,
    summary="Update user",
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    # Check if user exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    try:
        # Check email uniqueness if email is being updated
        if user_update.email and user_update.email != db_user.email:
            if db.query(User).filter(User.email == user_update.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

        # Update user
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

        return {"message": f"Update user successfully", "data": db_user}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{user_id}",
    response_model=dict,
    summary="Delete user",
    status_code=status.HTTP_200_OK,  # Changed from 204 to 200 to allow response body
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    # Check if user exists and prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
        )

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    try:
        db.delete(db_user)
        db.commit()
        return {"message": f"Delete user successfully", "data": {"id": user_id}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
