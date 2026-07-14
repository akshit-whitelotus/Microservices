from pydantic import BaseModel

class TaskCreate(BaseModel):
    title:str
    description:str
    user_id:int

class TaskResponse(TaskCreate):
    id:int
 

    class Config:
        from_attributes=True
    