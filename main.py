from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/yaly.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
