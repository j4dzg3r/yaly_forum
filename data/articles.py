import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Article(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'article'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    markdown_content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_change_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = sqlalchemy.orm.relationship('User', back_populates='articles')

    categories = sqlalchemy.orm.relationship('Category', secondary='association', backref='article')
