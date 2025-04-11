from fastapi import APIRouter

from app.modules.dataset.api import project, file, chunk, question

router = APIRouter()

router.include_router(project.router, prefix="/projects")
router.include_router(file.router, prefix="/files")
router.include_router(chunk.router, prefix="/chunks")
router.include_router(question.router, prefix="/questions")