import sqlalchemy

from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class Role(SqlAlchemyBase):
    __tablename__ = 'role'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
