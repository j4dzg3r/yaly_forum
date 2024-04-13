from flask import (Flask, render_template, redirect)
from flask_login import (LoginManager, login_user, login_required,
                         logout_user)

from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from flask_login import LoginManager
from flask_restful import reqparse, abort, Api, Resource
from forms.revision import RevisionForm

from data import db_session
from data.revisions import Revision
from data.articles import Article
from data.users import User

from forms.user import UserSignInForm, UserSignUpForm
from forms.revision import RevisionForm
from datetime import datetime
import os

from datetime import datetime, timedelta


template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
login_manager = LoginManager()
login_manager.init_app(app)
HOST = '127.0.0.1'
PORT = 8080


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
api = Api(app)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = UserSignInForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template("sign_in_user.html", message="Incorrect email or password", form=form)
    return render_template("sign_in_user.html", form=form, title="Sign In")


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = UserSignUpForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User()
        user.email = form.email.data
        user.set_password(form.password.data)
        user.nickname = form.nickname.data
        user.age = form.age.data
        user.description = form.description.data
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template("sign_up_user.html", form=form, title="Sign Up")


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


@app.route('/wiki')
def wiki():
    return render_template("base.html", title="Wiki")


@app.route('/')
def index():
    return redirect('/wiki')


def main() -> None:
    db_session.global_init("db/yaly.sqlite")
    app.run(host=HOST, port=PORT, debug=True)


if __name__ == "__main__":
    main()
