from flask import jsonify
from flask_restful import Resource

from data import db_session
from data.articles import Article
from data.revisions import Revision


class ArticleAPI(Resource):
    def get(self, article_id):
        sess = db_session.create_session()
        res = (sess.query(Article)
               .join(Revision)
               .filter(Article.id == article_id)
               .filter_by(verified=False)
               .order_by(Revision.created_at.desc())
               .first())
        if res:
            return jsonify({
                "article_id": res.id,
                "title": res.title,
                "content": res.revisions.markdown_content,
                "created_at": res.revisions.created_at,
                "author_id": res.revisions.author_id
            })
