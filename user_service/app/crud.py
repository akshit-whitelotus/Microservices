from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate

def create_user(db:Session,user:UserCreate):
    db_user=User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db:Session,user_id:int):
    return db.query(User).filter(User.id==user_id).first()

