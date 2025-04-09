from typing import List

from fastapi import APIRouter

from app.lib.db import get_projects, create_project
from app.modules.dataset.schema.project import ProjectInDB

router = APIRouter()

@router.get("", response_model=List[ProjectInDB])
async def project_list():
    projects = await get_projects()
    return projects

@router.get("/{id}", response_model=ProjectInDB)
async def project_get(id: int):
    pass

@router.post("")
async def project_create(project: ProjectInDB):
    await create_project({"name": project.name})
    return "ok"