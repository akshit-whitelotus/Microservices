from fastapi import FastAPI
from .database import engine
from .models import Base
from .routes import router as task_router

Base.metadata.create_all(bind=engine)

app=FastAPI()

app.include_router(task_router,prefix="/tasks",tags=["tasks"])

@app.get("/")
def read_root():
    return {"message":"Welcome to task service"}