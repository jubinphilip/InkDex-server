from fastapi import FastAPI

import models
from routers.users import router as users_router

app = FastAPI()

app.include_router(users_router)

