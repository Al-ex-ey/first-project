from fastapi import APIRouter

from src.api.endpoints import index_router


main_router = APIRouter()
# main_router.include_router(load_files_router, tags=['Files'])
main_router.include_router(index_router, tags=['Index'])
# main_router.include_router(user_router)
