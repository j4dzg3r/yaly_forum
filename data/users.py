import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase, create_session
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Self


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'user'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.Integer, default=None)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @staticmethod
    def get_by_id(_id: int):
        sess = create_session()
        return sess.query(User).filter_by(id=_id).first()

    @staticmethod
    def get_all_users():
        sess = create_session()
        return sess.query(User).all()


