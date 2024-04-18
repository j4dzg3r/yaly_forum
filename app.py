from flask import (Flask, render_template, redirect, render_template, redirect, request, render_template_string, jsonify)
from flask_login import (LoginManager, login_user, login_required, logout_user, current_user)

from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.revisions import Revision
from data.articles import Article
from data.users import User
from forms.search import SearchForm

from forms.user import UserSignInForm, UserSignUpForm
from forms.revision import RevisionForm

from api.articles import ArticleAPI

from datetime import datetime, timedelta
from markdown import markdown
from markdownify import markdownify

from tools.nlp import tokenize


template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.json.sort_keys = False
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.article_index = {}
api = Api(app)
api.add_resource(ArticleAPI,
                 '/articles/id/<int:article_id>',
                 '/articles/<string:article_title>',
                 "/articles")
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


def hu(html, content):
    return html.replace("~hu~", content)


@app.route('/wiki/<string:title>', methods=['GET', 'POST'])
def article(title):
    form = RevisionForm()
    action = request.args.get('action')
    oldid = request.args.get('oldid')
    db_sess = db_session.create_session()
    article_exist = (title,) in list(db_sess.query(Article.title).all())
    if article_exist:
        article = db_sess.query(Article).filter(Article.title == title).first()
        if request.method == "GET" and article_exist:
            form.content.data = markdownify(article.revisions[-1].markdown_content)
    if action == "edit":
        if form.validate_on_submit():
            if not article_exist:
                article = Article(
                    title=title
                )
                db_sess.add(article)
            md_to_html = markdown(form.content.data)
            revision = Revision(
                # author_id=current_user.id,
                author_id=1,
                article_id=article.id,
                created_at=datetime.now(),
                description=form.description.data,
                markdown_content=md_to_html,
                verified=False
            )

            article.revisions.append(revision)
            db_sess.merge(article)
            db_sess.commit()
            app.article_index[tokenize(title)] = article.id
            return redirect(f'/wiki/{title}')
        return render_template('revision.html',
                               answer=article_exist,
                               title=title,
                               form=form)
    elif action == "history":
        revisions = db_sess.query(Revision).filter(Revision.article_id == article.id).all()
        nick = db_sess.query(Revision).filter(Revision.article_id == article.id).first().author.nickname
        print(nick)
        return render_template('history.html',
                               answer=article_exist,
                               title=title,
                               revisions=revisions)
    else:
        if article_exist:
            article = db_sess.query(Article).filter(Article.title == title).first()
            last_rev = db_sess.query(Revision).filter(Revision.article_id == article.id).all()[-1]

            html = open("templates/article.html", encoding="utf8")
            if oldid:
                rev = db_sess.query(Revision).filter(Revision.id == oldid).first()
            else:
                rev = last_rev
            html_lines = hu("".join(list(html.readlines())), rev.markdown_content)
            html.close()
            return render_template_string(html_lines,
                                          title=title,
                                          answer=True,
                                          is_old=["cur", "?old", "?cur"][int(oldid is not None) + int(oldid is not None and int(oldid) == last_rev.id)],
                                          old_rev=rev)
        else:
            return render_template('article.html', title=title, answer=False)


@app.route('/lol')
def lol():
    return render_template('article.html')


@app.route('/wiki', methods=["GET", "POST"])
def wiki():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{form.search.data}")
    return render_template("index.html", form=form, title="Wiki")


@app.route('/search/<string:search>')
def search(search: str):
    ids = []
    search_token = tokenize(search)
    for i, j in app.article_index.items():
        if len(search_token & i) > 0:
            ids.append(j)
    sess = db_session.create_session()
    articles = sess.query(Article).filter(Article.id.in_(ids)).all()
    return render_template("search_results.html", articles=articles)


@app.route('/')
def index():
    return redirect('/wiki')


def main() -> None:
    db_session.global_init("db/yaly.sqlite")
    sess = db_session.create_session()
    articles = sess.query(Article).all()
    for article in articles:
        app.article_index[tokenize(article.title)] = article.id
    app.run(host=HOST, port=PORT, debug=True)


if __name__ == "__main__":
    main()
