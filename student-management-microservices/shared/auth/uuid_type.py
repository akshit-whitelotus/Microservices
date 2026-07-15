

from __future__ import annotations
import uuid
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import CHAR
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True
    def load_dialect_impl(self, dialect):

        if dialect.name == "postgresql":

            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))
    def process_bind_param(self,value,dialect,):
        if value is None:
            return value
        if dialect.name == "postgresql":
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))
        return str(value)

    def process_result_value(self,value,dialect,):
        if value is None:
            return value
        return uuid.UUID(str(value))