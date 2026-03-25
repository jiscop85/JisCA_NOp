from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "pending"

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    owner_id: int

    model_config = {
        "from_attributes": True
    }