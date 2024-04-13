from flask import jsonify
from flask_restful import Resource

from data import db_session
from data.articles import Article
from data.revisions import Revision


class ArticleAPI(Resource):
    def get(self, post_id):
        sess = db_session.create_session()
        res = (sess.query(Article)
               .join(Revision)
               .get(post_id)
               .filter_by(verified=True)
               .order_by(Revision.created_at.desc())
               .first())
        if res:
            return jsonify({
                "id": res.id,
                "title": res.title,
                "content": res.revisions.markdown_content,
                "created_at": res.revisions.created_at
            })
