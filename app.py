from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from flask_login import LoginManager
from flask_restful import reqparse, abort, Api, Resource
from forms.revision import RevisionForm

from data import db_session
from data.revisions import Revision
from data.articles import Article
from datetime import datetime
import os

template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
api = Api(app)


# login_manager = LoginManager()
# login_manager.init_app(app)


@app.route('/article/<string:title>', methods=['GET', 'POST'])
def make_revision(title):
    form = RevisionForm()
    db_sess = db_session.create_session()
    is_new = title not in map(lambda x: x.title, list(db_sess.query(Article).all()))
    if form.validate_on_submit():
        article = Article(
            title=title
        )

        revision = Revision(
            author_id=1,
            article_id=article.id,
            created_at=datetime.now(),
            markdown_content=form.content.data,
            verified=False
        )

        if is_new:
            db_sess.add(article)
        else:
            article = db_sess.query(Article).filter(Article.title == title).first()

        article.revisions.append(revision)
        db_sess.merge(article)
        db_sess.commit()
        return redirect('/a')
    return render_template('revision.html',
                           title=[f"Создание страницы «{title}»", f"Редактирование: {title}"][not is_new],
                           form=form)


def main() -> None:
    db_session.global_init("db/ yaly.sqlite")
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
