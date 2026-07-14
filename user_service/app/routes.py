from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate,UserResponse
from app.crud import create_user,get_user

router=APIRouter()

@router.post("/users",response_model=UserResponse)
def create(user:UserCreate,db:Session=Depends(get_db)):
    return create_user(db,user)

@router.get("/users/{user_id}",response_model=UserResponse)
def read(user_id:int,db:Session=Depends(get_db)):
    user=get_user(db,user_id)
    if not user :
        raise HTTPException(status_code=404,detail="User not Found")
    return user

