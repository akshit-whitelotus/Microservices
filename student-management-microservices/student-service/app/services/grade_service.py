from __future__ import annotations
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import NotFoundException,BadRequestException
from app.repositories.grade_repository import GradeRepository
from app.schemas.grade import GradeUpsertItem,BulkUpsertResult

logger=logging.getLogger(__name__)

class GradeService:
    def __init__(self) -> None:
        self.repository=GradeRepository()
    def bulk_upsert(self,db:Session,items:list[GradeUpsertItem])->BulkUpsertResult:
        if not items :
            raise BadRequestException(message="Grade upload cannot be empty")
        try:
            created,updated,missing_ids=(self.repository.bulk_upsert(db=db,rows=items))
            db.commit()
            return BulkUpsertResult(
                created=created,
                updated=updated,
                not_found_student_ids=missing_ids
            )
            
        except SQLAlchemyError as exc :
            db.rollback()
            logger.exception("Grade bulk upload failed")
            raise BadRequestException(
                "unable to procss grade upload"
            )from exc
    def list_students_grades(self,db:Session,student_id:int):
        grades=(self.repository.list_for_student(db=db,student_id=student_id))
        return grades