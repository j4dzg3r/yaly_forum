from flask import jsonify
from flask_restful import Resource

from data import db_session
from data.articles import Article
from data.revisions import Revision


def get_by_id(article_id):
    sess = db_session.create_session()
    res = (sess.query(Article)
           .join(Revision)
           .filter(Article.id == article_id)
           .filter_by(verified=True)
           .order_by(Revision.created_at.desc())
           .first())
    return res


def get_by_title(article_title):
    sess = db_session.create_session()
    res = (sess.query(Article)
           .join(Revision)
           .filter(Article.title == article_title)
           .filter_by(verified=True)
           .order_by(Revision.created_at.desc())
           .first())
    return res


def get_all():
    sess = db_session.create_session()
    res = (sess.query(Article)
           .join(Revision)
           .all())
    return res


class ArticleAPI(Resource):
    def get(self, article_id=None, article_title=None):
        if article_id:
            res = get_by_id(article_id)
        elif article_title:
            res = get_by_title(article_title)
        else:
            res = get_all()
            ret = []
            for entity in res:
                j = {
                    "article_id": entity.id,
                    "title": entity.title,
                    "message": "Article successfully retrieved",
                    "revisions": []
                }
                for rev in entity.revisions:
                    j["revisions"].append({
                        "content": rev.markdown_content,
                        "created_at": rev.created_at,
                        "author_id": rev.author_id,
                        "verified": rev.verified
                    })
                ret.append(j)
            return jsonify(ret)
        if res:
            return jsonify({
                "article_id": res.id,
                "title": res.title,
                "content": res.revisions[0].markdown_content,
                "created_at": res.revisions[0].created_at,
                "author_id": res.revisions[0].author_id,
                "message": "Article successfully retrieved",
                "verified": res.revisions[0].verified
            })
        return jsonify({"message": "Article not found"})
