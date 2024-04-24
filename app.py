from flask import (Flask, render_template, redirect, render_template, redirect, request, render_template_string)
from flask_login import (LoginManager, login_user, login_required, logout_user, current_user)

from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.revisions import Revision
from data.articles import Article
from data.users import User

from forms.user import UserSignInForm, UserSignUpForm
from forms.revision import RevisionForm

from api.articles import ArticleAPI

from datetime import datetime, timedelta
from markdown import markdown
from markdownify import markdownify
import difflib

template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.json.sort_keys = False
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
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


def hu(file, content):
    html = open(f"templates/{file}", encoding="utf8")
    html_lines = "".join(list(html.readlines()))
    html.close()
    return html_lines.replace("~hu~", content)


def differences(txt1, txt2):
    txt1_list = txt1.splitlines()
    txt2_list = txt2.splitlines()
    print(txt1_list)
    print(txt2_list)
    differ = difflib.Differ()
    diff = differ.compare(txt1_list, txt2_list)
    diff_list = []
    for i in diff:
        diff_list.append([i[:1], i[2:]])
    print(diff_list)
    out = ""
    for i in diff_list:
        if i[0] == " ":
            color = "white"
            i[0] = "."
        elif i[0] == "-":
            color = "red"
        elif i[0] == "+" or i[0] == "?":
            color = "yellow"
        out += f"<p> <span style='background-color:{color}; line-height: 0.9em'>{i[0]} </span>{i[1]}</p>"
    return out


@app.route('/wiki/<string:title>', methods=['GET', 'POST'])
def article(title):
    form = RevisionForm()
    action = request.args.get('action')
    oldid = request.args.get('oldid')
    diff = request.args.get('diff')
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
            revision = Revision(
                author_id=current_user.id,
                article_id=article.id,
                created_at=datetime.now(),
                description=form.description.data,
                markdown_content=form.content.data,
                verified=False
            )

            article.revisions.append(revision)
            db_sess.merge(article)
            db_sess.commit()
            return redirect(f'/wiki/{title}')
        return render_template('revision.html',
                               answer=article_exist,
                               title=title,
                               form=form)
    elif action == "history":
        revisions = db_sess.query(Revision).filter(Revision.article_id == article.id).all()
        if request.method == 'POST':
            first_rev_id = request.form['first_rev'][2:]
            second_rev_id = request.form['second_rev'][2:]
            return redirect(f"{first_rev_id}+{second_rev_id}")
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
            if diff:
                if not oldid:
                    revisions = db_sess.query(Revision).filter(Revision.article_id == article.id).all()
                    # Если не oldid не задан - сравнение с предпоследней версией
                    for i in range(len(revisions)):
                        if revisions[i].id == int(diff):
                            oldid = i
                else:
                    oldid = int(oldid)
                old_rev = db_sess.query(Revision).filter(Revision.id == oldid).first()
                content = differences(old_rev.markdown_content, last_rev.markdown_content).replace("\n", "<br>")
                html_lines = hu("article.html", content)
                print([content])
                return render_template_string(html_lines,
                                              title=title,
                                              answer=True)

            if oldid:
                rev = db_sess.query(Revision).filter(Revision.id == oldid).first()
            else:
                rev = last_rev
            content = rev.markdown_content
            html_lines = hu("article.html", markdown(content))
            return render_template_string(html_lines,
                                          title=title,
                                          answer=True,
                                          is_old=["cur", "?old", "?cur"][int(oldid is not None) + int(
                                              oldid is not None and int(oldid) == last_rev.id)],
                                          old_rev=rev)
        else:
            return render_template('article.html', title=title, answer=False)


@app.route('/lol')
def lol():
    return render_template('article.html')


@app.route('/wiki')
def wiki():
    return redirect("/wiki/Заглавная страница")


@app.route('/')
def index():
    return redirect('/wiki')


def main() -> None:
    db_session.global_init("db/yaly.sqlite")
    app.run(host=HOST, port=PORT, debug=True)


if __name__ == "__main__":
    main()
