from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_superuser, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


@router.get("/", summary="Get users list")
async def get_users(
    offset=0,
    limit=10,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    users = db.query(User).offset(offset).limit(limit).all()
    return {"message": "Get users list successfully", "data": users}


@router.get("/{user_id}", summary="Get user detail")
async def get_user(
    user_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    user = db.query(User).filter(User.id == user_id).first()
    return {"message": "Get user detail successfully", "data": user}


@router.post("/", summary="Create user")
async def create_user(
    user: UserCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.add(User(**user.dict()))
    db.commit()
    db.refresh(user)
    return {"message": "Create a user successfully", "data": user}


@router.put("/{user_id}", summary="Update user")
async def update_user(
    user_id: int,
    user: UserUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(User).filter(User.id == user_id).update(user.dict())
    db.commit()
    return {"message": f"Update user successfully, user ID: {user_id}"}


@router.delete("/{user_id}", summary="Delete user")
async def delete_user(
    user_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    return {"message": f"Delete user successfully, user ID: {user_id}"}
