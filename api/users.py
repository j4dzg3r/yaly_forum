from flask import jsonify
from flask_restful import Resource, reqparse

from app.app import app
from data.users import User


parser = reqparse.RequestParser()
parser.add_argument('nickname', required=True)
parser.add_argument("password", required=True)
parser.add_argument("email", required=True)
parser.add_argument("age", required=False)
parser.add_argument("description", required=False)


class Login(Resource):
    def post(self):
        pass


class Register(Resource):
    def post(self):
        pass