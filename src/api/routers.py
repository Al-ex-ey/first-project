from fastapi import APIRouter

from src.api.endpoints import load_files_router


main_router = APIRouter()
main_router.include_router(
    load_files_router, prefix='/files', tags=['Files']
)
# main_router.include_router(user_router)
