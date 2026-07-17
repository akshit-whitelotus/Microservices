from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel,Field,ConfigDict

class GradeUpsertItem(BaseModel):
    student_id:int=Field(...,gt=0)
    subject:str=Field(...,min_length=1, max_length=100)
    marks:float=Field(...,ge=0)
    max_marks:float=Field(...,default=100,gt=0)
    exam_term:str=Field(...,min_length=1,max_length=100)
    source_document_id:str=Field(...,min_length=1,max_length=64)
    uploaded_by:int=Field(...,gt=0)

class BulkUpsertRequest(BaseModel):
    items:list[GradeUpsertItem]

class BulkUpsertResult(BaseModel):
    created_at:int
    updated:int
    not_found_student_ids:list[int]

class GradeResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    student_id:int
    subject:int
    marks:float
    max_marks:float
    exam_term:str
    source_document_id:str
    uploaded_by:int
    created_at:datetime
    updated_at:datetime