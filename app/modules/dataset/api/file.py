from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.core.texts import save_file, get_files, get_file_by_hash

router = APIRouter()

@router.get("")
async def get_file_list():
    project_id = "000000"
    ret = await get_files(project_id)
    return ret

@router.get("/{file_hash}")
async def file_by_hash(file_hash: str):
    project_id = "000000"
    return await get_file_by_hash(project_id, file_hash)


@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """
    接收并解析上传的文件
    """
    try:
        # 读取文件内容
        contents = await file.read()

        project_id = "000000"
        ret = await save_file(project_id, contents, file.filename)
        
        # 返回解析结果
        return JSONResponse({
            "filename": file.filename,
            "content_type": file.content_type,
            "file_path": ret["path"],
            "size": len(contents),
            # "parsed_content": parsed_content  # 实际解析后的内容
        })
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
