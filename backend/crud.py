from sqlalchemy.orm import Session
from models import Task

def get_tasks(db: Session, search: str = ""):
    return db.query(Task).filter(Task.title.contains(search)).all()
def create_task(db: Session, task):
    new_task = Task(title=task.title, status=task.status)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

