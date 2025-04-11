from fastapi import APIRouter, HTTPException

from app.core.text_splitter import split_project_file
from app.core.texts import get_text_chunk_ids

router = APIRouter()

@router.get("")
async def get_text_chunks():
    project_id = "000000"
    ret = await get_text_chunk_ids(project_id)
    return ret

@router.post("/file_chunk_by_hash/{file_hash}")
async def chunk_file_by_hash(file_hash: str):
    project_id = "000000"
    try:
        ret = await split_project_file(project_id, file_hash)
        return ret
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

