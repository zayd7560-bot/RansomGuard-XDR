from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/download", tags=["Download"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

@router.get("/windows")
def download_windows():

    file_path = os.path.join(BASE_DIR, "dist", "RansomGuard.exe")

    return FileResponse(
        file_path,
        filename="RansomGuard.exe",
        media_type="application/octet-stream",
    )