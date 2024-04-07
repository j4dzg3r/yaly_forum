from flask import Flask
from flask_login import LoginManager
from flask_restful import reqparse, abort, Api, Resource

from data import db_session

app = Flask(__name__)
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


def main() -> None:
    db_session.global_init("../db/yaly.sqlite")
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
