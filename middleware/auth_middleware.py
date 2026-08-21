import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from security.jwt import decode_access_token

PUBLIC_PATHS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/login",
    "/users/create-user",
}


def unauthorized_response(detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return unauthorized_response("Missing or invalid Authorization header")

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            request.state.user_id = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return unauthorized_response("Token has expired")
        except (jwt.InvalidTokenError, ValueError, KeyError):
            return unauthorized_response("Invalid token")

        return await call_next(request)
