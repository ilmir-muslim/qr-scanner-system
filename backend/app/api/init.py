from fastapi import APIRouter
from app.api.endpoints import scans, printers, export

api_router = APIRouter()

api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(printers.router, prefix="/printers", tags=["printers"])
