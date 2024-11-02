from fastapi import FastAPI

from Domain.DB.router import router as DB_router
from Domain.Business.router import router as Business_router

app = FastAPI()
app.include_router(DB_router)
app.include_router(Business_router)
