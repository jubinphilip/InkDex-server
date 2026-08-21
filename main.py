from fastapi import FastAPI

import models
from middleware.auth_middleware import AuthMiddleware
from routers.auth import router as auth_router
from routers.document import router as document_router
from routers.users import router as users_router

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(document_router)
