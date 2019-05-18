import json
import os
from flask import current_app

import time, bcrypt
from flask import request, current_app, g, abort
from flask_restful import Resource
import social.utils.auth
from social.schemas import UserSchema, UserLoginSchema
from social import model, schemas, exception, utils
from social.exception import  DataInvaliError, LoginFailError
from marshmallow import ValidationError

__all__ = [
    'Register',
    "Login"
]

user_schema = UserSchema()
user_login = UserLoginSchema()

class Register(Resource):
    """创建用户"""
    def post(self):
        current_app.logger.info("resiter user")

        if request.get_json() is None:
            raise DataInvaliError("你没有数据")
        user_data = user_schema.load(request.get_json())

        if user_data.errors:
            raise DataInvaliError(str(user_data.errors))

        user_data.data.password = bcrypt.hashpw(user_data.data.password.encode(), bcrypt.gensalt())
        model.db.session.add(user_data.data)
        model.db.session.commit()

        user_data = user_schema.dump(user_data.data)
        if user_data.errors:
            raise DataInvaliError(str(user_data.errors))

        return utils.ok(user_data.data)

class Login(Resource):
    def post(self):
        if request.get_json() is None:
            raise DataInvaliError("你没有数据")
        ul = user_schema.load(request.get_json())


