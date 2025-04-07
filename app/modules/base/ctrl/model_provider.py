from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def get_providers():
    return "hello"

