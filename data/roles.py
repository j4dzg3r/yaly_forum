import sqlalchemy

from data.db_session import SqlAlchemyBase


class Role(SqlAlchemyBase):
    __tablename__ = 'role'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
