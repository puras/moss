from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class User(BaseModel):
    id: int
    name: str
    email: str

# 模拟数据
users_db = [
    User(id=1, name="张三", email="zhangsan@example.com"),
    User(id=2, name="李四", email="lisi@example.com")
]

@router.get("/", response_model=list[User])
async def get_users():
    return users_db

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="用户不存在")