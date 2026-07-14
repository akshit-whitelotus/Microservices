from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TaskCreate,TaskResponse
from app.crud import create_task
from app.services.user_client import verify_user

router=APIRouter()
@router.post("/tasks",response_model=TaskResponse)
async def create(task:TaskCreate,db:Session=Depends(get_db)):
    await verify_user(task.user_id)
    return create_task(db,task)
