import uuid

from fastapi import HTTPException, Request, status


def get_current_user_id(request: Request) -> uuid.UUID:
    user_id = getattr(request.state, "user_id", None)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return user_id
