from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



from Domain.DB.iPhone14_processed_info.router import router as iPhone14_processed_info_router
from Domain.Business.router import router as Business_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(iPhone14_processed_info_router)
app.include_router(Business_router)
