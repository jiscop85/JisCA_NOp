from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.crud.task import get_tasks, get_task, create_task, update_task, delete_task

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=list[TaskOut])
def list_tasks(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_tasks(db, owner_id=current_user.id, search=search)

@router.post("/", response_model=TaskOut)
def add_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_task(
        db,
        owner_id=current_user.id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status
    )

