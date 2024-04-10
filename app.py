from flask import (Flask, render_template, redirect)
from flask_login import (LoginManager, login_user, login_required,
                         logout_user)

from data import db_session
from data.revisions import Revision
from data.articles import Article
from data.users import User

from forms.user import UserSignInForm, UserSignUpForm
from forms.revision import RevisionForm

from datetime import datetime, timedelta


app = Flask(__name__)
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
    return render_template('revision.html', title='Новая статья', form=form)


@app.route('/')
def index():
    return render_template("base.html", title="Yaly")


def main() -> None:
    db_session.global_init("db/yaly.sqlite")
    app.run(host=HOST, port=PORT, debug=True)


if __name__ == "__main__":
    main()
