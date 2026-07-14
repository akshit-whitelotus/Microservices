from sqlalchemy.orm import Session
from app.models import Task
from app.schemas import TaskCreate

def create_task(db:Session, task:TaskCreate):
    db_task=Task(**task.model_dump())

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
