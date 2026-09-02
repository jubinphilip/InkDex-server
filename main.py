from fastapi import FastAPI

import models
from middleware.auth_middleware import AuthMiddleware
from routers.auth import router as auth_router
from routers.document import router as document_router
from routers.users import router as users_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://inkdex-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(document_router)
