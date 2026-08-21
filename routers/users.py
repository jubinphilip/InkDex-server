from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.user_credentials import UserCredentials
from schemas.user_response import UserResponse
from services.user_service import create_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/create-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_route(
    user: UserCredentials,
    db: Session = Depends(get_db),
):
    return create_user(db, user)
