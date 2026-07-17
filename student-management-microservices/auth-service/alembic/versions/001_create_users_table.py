"""create users table"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_users"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None



def upgrade():

    op.create_table(
        "users",
        sa.Column("id",sa.Integer(),primary_key=True,nullable=False,),
        sa.Column("username",sa.String(length=100),nullable=False,),
        sa.Column("email",sa.String(length=255),nullable=False,),
        sa.Column("hashed_password",sa.String(length=255),nullable=False,),
        sa.Column("role",sa.String(length=30),nullable=False,server_default="student",),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true(),),
        sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),),
        sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),),
    )
    op.create_index("ix_users_username","users",["username"],unique=True,)
    op.create_index("ix_users_email","users",["email"],unique=True,)

def downgrade():

    op.drop_table(
        "users"
    )