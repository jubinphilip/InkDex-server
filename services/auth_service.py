from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.user_repository import get_user_by_email
from schemas.token_response import TokenResponse
from schemas.user_credentials import UserCredentials
from security.jwt import create_access_token
from security.password import verify_password


def login_user(db: Session, credentials: UserCredentials) -> TokenResponse:
    user = get_user_by_email(db, credentials.email)

    if user is None or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(access_token=create_access_token(user.id))
