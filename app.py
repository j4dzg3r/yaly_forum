from flask import (Flask, render_template, redirect, render_template, redirect, request, render_template_string)
from flask_login import (LoginManager, login_user, login_required, logout_user, current_user)

from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.revisions import Revision
from data.articles import Article
from data.users import User
from data.roles import Role
from forms.search import SearchForm

from forms.user import UserSignInForm, UserSignUpForm
from forms.revision import RevisionForm
from forms.to_verificate import VerifyForm

from api.articles import ArticleAPI

from datetime import datetime, timedelta
from markdown import markdown
from markdownify import markdownify
import difflib

from tools.nlp import tokenize
import nltk

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
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")
    sign_in_form = UserSignInForm()
    if sign_in_form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == sign_in_form.email.data).first()
        if user and user.check_password(sign_in_form.password.data):
            login_user(user, remember=sign_in_form.remember_me.data)
            return redirect('/')
        return render_template("sign_in_user.html", message="Incorrect email or password", form=sign_in_form, search_form=search_form)
    return render_template("sign_in_user.html", sign_in_form=sign_in_form, title="Sign In", search_form=search_form)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")
    sign_up_form = UserSignUpForm()
    if sign_up_form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User()
        user.email = sign_up_form.email.data
        user.set_password(sign_up_form.password.data)
        user.nickname = sign_up_form.nickname.data
        user.age = sign_up_form.age.data
        user.description = sign_up_form.description.data
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template("sign_up_user.html", sign_up_form=sign_up_form, title="Sign Up", search_form=search_form)


def detect_templates(file_name: str, hu_content: str) -> str:
    out = open(f"templates/{file_name}", encoding="utf8").read().replace("~hu~", hu_content)

    # all articles
    db_sess = db_session.create_session()
    all_articles_list = list(db_sess.query(Article.title, Article.id).all())
    all_articles = f"""<div style="border: 3px #CDCDCD solid; padding: 10px">
                   <h3 style="">All articles on Wikipedia ({len(all_articles_list)})</h3>"""
    for article in all_articles_list:
        all_articles += '''<div style="display: flex; justify-content: space-between;">\n'''
        last_rev = db_sess.query(Revision).filter(Revision.article_id == article[1]).all()[-1]
        all_articles += f"""<span><a href="/wiki/{article[0]}">{article[0]}</a> ({len(last_rev.markdown_content)})</span>
        <span><a href="/wiki/User:{last_rev.author.nickname}">{last_rev.author.nickname}</a></span>
        </div>"""

    out = out.replace("~all articles~", all_articles)
    return out


def differences(txt1: str, txt2: str) -> str:
    txt1_list = txt1.splitlines()
    txt2_list = txt2.splitlines()
    differ = difflib.Differ()
    diff = differ.compare(txt1_list, txt2_list)
    diff_list = []
    for i in diff:
        diff_list.append([i[:1], i[2:]])
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
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")

    title = title.replace("_", " ")
    revision_form = RevisionForm()
    action = request.args.get('action')
    oldid = request.args.get('oldid')
    diff = request.args.get('diff')
    db_sess = db_session.create_session()
    article_exist = (title,) in list(db_sess.query(Article.title).all())
    if article_exist:
        article = db_sess.query(Article).filter(Article.title == title).first()
        if request.method == "GET" and article_exist:
            revision_form.content.data = markdown(article.revisions[-1].markdown_content)
    if action == "edit":
        if revision_form.validate_on_submit():
            if not article_exist:
                article = Article(
                    title=title
                )
                db_sess.add(article)
            revision = Revision(
                author_id=current_user.id if current_user.is_authenticated else 0,
                article_id=article.id,
                created_at=datetime.now(),
                description=revision_form.description.data,
                markdown_content=revision_form.content.data,
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
                               form=revision_form,
                               search_form=search_form)
    elif action == "history":
        revisions = db_sess.query(Revision).filter(Revision.article_id == article.id).all()
        if request.method == 'POST':
            first_rev_id = request.form['first_rev'][2:]
            second_rev_id = request.form['second_rev'][2:]
            return redirect(f"{first_rev_id}+{second_rev_id}")
        return render_template('history.html',
                               answer=article_exist,
                               title=title,
                               revisions=revisions,
                               search_form=search_form)
    else:
        if article_exist:
            article = db_sess.query(Article).filter(Article.title == title).first()
            last_rev = db_sess.query(Revision).filter(Revision.article_id == article.id).all()[-1]
            if diff:
                if not oldid:
                    revisions = db_sess.query(Revision).filter(Revision.article_id == article.id).all()
                    # If oldid is not specified, the comparison will be made with the previous version.
                    for i in range(len(revisions)):
                        if revisions[i].id == int(diff):
                            oldid = i
                else:
                    oldid = int(oldid)
                old_rev = db_sess.query(Revision).filter(Revision.id == oldid).first()
                content = differences(old_rev.markdown_content, last_rev.markdown_content).replace("\n", "<br>")
                html_lines = detect_templates("article.html", content)
                return render_template_string(html_lines,
                                              title=title,
                                              answer=True,
                                              search_form=search_form)

            if oldid:
                rev = db_sess.query(Revision).filter(Revision.id == oldid).first()
            else:
                rev = last_rev
            content = rev.markdown_content
            html_lines = detect_templates("article.html", markdown(content))
            old = ["cur", "?old", "?cur"][int(oldid is not None) + int(oldid is not None and int(oldid) == last_rev.id)]
            return render_template_string(html_lines,
                                          title=title,
                                          answer=True,
                                          is_old=old,
                                          old_rev=rev,
                                          search_form=search_form)
        else:
            return render_template('article.html', title=title, answer=False, search_form=search_form)


@app.route('/wiki/revision/<int:revision_id>', methods=['GET', 'POST'])
def article_revision(revision_id):
    form = VerifyForm()
    sess = db_session.create_session()
    if form.validate_on_submit():
        sess.query(Revision). \
            filter(Revision.id == revision_id). \
            update({'verified': form.verify.data})
        sess.commit()
    is_moder = False
    u, r = sess.query(User, Role).filter(User.id == current_user.get_id()).first()
    if u and r.role in ["moderator", "admin"]:
        is_moder = True
    revision = sess.query(Revision).filter(Revision.id == revision_id).join(Article).first()
    form.verify.data = revision.verified
    if revision:
        html_res = detect_templates("m_revision.html", markdown(revision.markdown_content))
        try:
            author = revision.author.nickname
        except AttributeError:
            author = "None"
        meta_info = {"author": author,
                     "date": revision.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
                     "description": revision.description}
        return render_template_string(html_res, meta_info=meta_info,
                                      title=revision.article_id, answer=True, is_moder=is_moder, form=form)
    html_res = detect_templates("m_revision.html", "")
    return render_template_string(html_res, meta_info={}, title=revision_id, answer=False, form=form)


@app.route('/wiki', methods=["GET", "POST"])
def wiki():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")
    return render_template("index.html", title="Wiki", search_form=search_form)


@app.route('/search/<string:search>')
def search(search: str):
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")
    ids = []
    search_token = tokenize(search)
    for i, j in app.article_index.items():
        if len(search_token & i) > 0:
            ids.append(j)
    sess = db_session.create_session()
    articles = sess.query(Article).filter(Article.id.in_(ids)).join(Revision).filter(Revision.verified == True).all()
    return render_template("search_results.html", articles=articles, search_form=search_form)


@app.route("/moderate")
def moderate():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")
    sess = db_session.create_session()
    user, role = sess.query(User, Role).filter(User.id == current_user.get_id()).first()
    if role.role not in ["moderator", "admin"]:
        return render_template("article.html", title="You cannot moderate articles.", answer=True)
    revisions_to_moderates = sess.query(Revision).filter(Revision.verified == False).all()
    return render_template("revisions_to_moderate.html", revisions=revisions_to_moderates, search_form=search_form)


@app.route('/')
def index():
    return redirect('/wiki/Main_page')


def main() -> None:
    nltk.download("punkt_tab")
    nltk.download("stopwords")
    db_session.global_init("db/yaly.sqlite")
    sess = db_session.create_session()
    articles = sess.query(Article).all()
    for article in articles:
        app.article_index[tokenize(article.title)] = article.id
    app.run(host=HOST, port=PORT, debug=True)


if __name__ == "__main__":
    main()
