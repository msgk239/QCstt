from fastapi import APIRouter
from server.services.file_service import FileService
from server.services.asr_service import ASRService

router = APIRouter()

@router.get("/api/files/{file_id}")
async def get_file_info(file_id: str):
    return file_service.get_file_detail(file_id)

@router.post("/api/asr/recognize")
async def start_recognition(file_id: str):
    return asr_service.start_recognition(file_id) 