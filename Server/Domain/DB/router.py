from fastapi import APIRouter

from Domain.DB.iPhone14_processed_info.router import router as iPhone14_processed_info_router

router = APIRouter(
    prefix="/DB",
    tags=["DB"]
)

router.include_router(iPhone14_processed_info_router)

