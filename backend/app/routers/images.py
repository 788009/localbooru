from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.indexer import indexer
from app.schemas import ImageDetail

router = APIRouter(prefix="/api/images", tags=["images"])

@router.get("/{img_id}/detail", response_model=ImageDetail)
def get_image_detail(img_id: str):
    detail = indexer.get_detail(img_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Image not found")
    return detail

@router.get("/{img_id}/file")
def get_image_file(img_id: str):
    detail = indexer.get_detail(img_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(detail["path"])
