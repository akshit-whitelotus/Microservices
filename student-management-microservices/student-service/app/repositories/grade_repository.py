from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.grade import Grade
from app.models.student import Student
from app.schemas.grade import GradeUpsertItem

class GradeRepository:
    def get_existing_student_ids(self,db:Session,student_ids:list[int])->set[int]:
        if not student_ids:
            return set()
        stmt=(select(Student.id).where(Student.id.in_(student_ids)))
        return set(db.scalars(stmt).all())
    def bulk_upsert(self,db:Session,rows:list[GradeUpsertItem],)->tuple[int,int,list[int]]:
        if not rows:
            return 0,0,[]
        student_ids=list({
            row.student_id
            for row in rows
        })
        existing_ids=(self.get_existing_student_ids(db=db,student_ids=student_ids))
        missing_ids=[sid for sid in student_ids if sid not in existing_ids]
        valid_rows=[row for row in rows if row.student_id in existing_ids]
        if not valid_rows :
            return (0,0,missing_ids)
        values=[row.model_dump() for row in valid_rows]
        stmt=insert(Grade).values(values)
        update_values={
            "marks":stmt.excluded.marks,
            "max_marks":stmt.excluded.max_marks,
            "source_document_id":stmt.excluded.source_document_id,
            "uploaded_by":stmt.excluded.uploaded_by,
            "updated_at":stmt.excluded.updated_at
        }
        stmt=(stmt.on_conflict_do_update(
            constraint="uq_grade_student_subject_term",
            set_=update_values
        ))
        result=db.execute(stmt)

        return (
            result.rowcount,
            0,
            missing_ids
        )
    def list_for_student(self,db:Session,student_id:int)->list[Grade]:
        stmt=(select(Grade).where(Grade.student_id==student_id).order_by(Grade.subject))
        return list(db.scalars(stmt).all())
    