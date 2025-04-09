from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str

class ProjectInDB(ProjectBase):
    id: int