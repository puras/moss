from fastapi import APIRouter

from app.modules.dataset.api import project

router = APIRouter()

router.include_router(project.router, prefix="/projects", tags=["dataset project"])