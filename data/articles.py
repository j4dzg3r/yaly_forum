import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Article(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'article'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    categories = sqlalchemy.orm.relationship('Category', secondary='association', backref='article')
    revisions = sqlalchemy.orm.relationship('Revision', back_populates='article')
