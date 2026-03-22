from sqlalchemy.orm import Session
from models import Task

def get_tasks(db: Session, search: str = ""):
    return db.query(Task).filter(Task.title.contains(search)).all()

