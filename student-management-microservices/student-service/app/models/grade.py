from __future__ import annotations
from datetime import datetime
from sqlalchemy import ForeignKey,Integer,String,Float,UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Base

class Grade(Base):
    __tablename__="grades"
    __table_args__= (
        UniqueConstraint(
            "student_id",
            "subject",
            "exam_term",
            name="uq_grade_subject_term"
        ),
    
    )
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    student_id:Mapped[int]=mapped_column(ForeignKey("students.id"),nullable=False,index=True)
    subject:Mapped[str]=mapped_column(String(100),nullable=False)
    marks:Mapped[float]=mapped_column(Float,nullable=False)
    max_marks:Mapped[float]=mapped_column(Float,default=100 ,nullable=False)
    exam_term:Mapped[str]=mapped_column(String(100),nullable=False)
    source_document_id:Mapped[str]=mapped_column(String(64),nullable=False)
    uploaded_by:Mapped[int]=mapped_column(Integer,nullable=False)
    created_at:Mapped[datetime]=mapped_column(server_default=func.now())
    updated_at:Mapped[datetime]=mapped_column(server_default=func.now(),onupdate=func.now())
