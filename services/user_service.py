from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from repositories.user_repository import create_user as create_user_record
from repositories.user_repository import get_user_by_email
from security.password import hash_password
from schemas.user_credentials import UserCredentials


def create_user(db: Session, user: UserCredentials):
    existing_user = get_user_by_email(db, user.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    try:
        return create_user_record(
            db=db,
            email=user.email,
            password=hash_password(user.password),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from None
