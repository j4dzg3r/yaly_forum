from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from flask_login import LoginManager
from flask_restful import reqparse, abort, Api, Resource
from forms.revision import RevisionForm

from data import db_session
from data.revisions import Revision
from data.articles import Article
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/new_article', methods=['GET', 'POST'])
def add_news():
    form = RevisionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        article = Article(
            title=form.title.data
        )
        revision = Revision(
            title=form.title.data,
            author_id=1,
            article_id=article.id,
            created_at=datetime.now(),
            markdown_content=form.content.data,
            verified=form.verified.data
        )
        db_sess.add(article)
        article.revisions.append(revision)
        db_sess.merge(article)
        db_sess.commit()
        return redirect('/')
    return render_template('D:\\yaly_wiki\\templates\\revision.html', title='Новая статья', form=form)


def main() -> None:
    db_session.global_init("../db/yaly.sqlite")
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
