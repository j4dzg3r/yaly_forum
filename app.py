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


@app.route('/wiki/<string:title>', methods=['GET', 'POST'])
def article(title):
    form = RevisionForm()
    is_editing = request.args.get('action') == "edit"
    oldid = request.args.get('oldid')
    db_sess = db_session.create_session()
    article_exist = (title,) in list(db_sess.query(Article.title).all())
    if article_exist:
        article = db_sess.query(Article).filter(Article.title == title).first()
        if request.method == "GET" and article_exist:
                form.content.data = article.revisions[-1].markdown_content
    if is_editing:
        if form.validate_on_submit():
            if not article_exist:
                article = Article(
                    title=title
                )
                db_sess.add(article)

            revision = Revision(
                author_id=1,
                article_id=article.id,
                created_at=datetime.now(),
                markdown_content=form.content.data,
                verified=False
            )

            article.revisions.append(revision)
            db_sess.merge(article)
            db_sess.commit()
            return redirect(f'/wiki/{title}')
        return render_template('revision.html',
                               title=[f"Создание страницы «{title}»", f"Редактирование: {title}"][article_exist],
                               form=form)
    else:
        if article_exist:
            article = db_sess.query(Article).filter(Article.title == title).first()
            markdown_content = db_sess.query(Revision).filter(Revision.article_id == article.id).all()[-1].markdown_content
            return render_template('article.html', title=title, markdown_content=markdown_content, answer=True)
        else:
            return render_template('article.html', title=title, answer=False)


def main() -> None:
    db_session.global_init("db/yaly.sqlite")
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
