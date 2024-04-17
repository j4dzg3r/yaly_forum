import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Revision(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'revision'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('article.id'))
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    markdown_content = sqlalchemy.Column(sqlalchemy.String)
    verified = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    description = sqlalchemy.Column(sqlalchemy.String)

    author = sqlalchemy.orm.relationship('User')
    article = sqlalchemy.orm.relationship('Article')
