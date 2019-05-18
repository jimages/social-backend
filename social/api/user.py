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

        if model.User.query.filter_by(username=user_data.data.username).first():
            raise DataInvaliError("该用户名已经存在，请重新选择")

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
        ul = user_login.load(request.get_json())
        if ul.errors:
            raise DataInvaliError("缺少登陆名字和账号")

        # 登陆验证
        user = model.User.getByUsername(ul.data['username'])
        if user is None:
            raise LoginFailError('密码错误或者账户不存在')

        current_app.logger.info("Login with password")
        re = user.checkPassword(ul.data['password'])
        if re is False:
            raise LoginFailError("密码错误或者账户不存在")

        # Now we generate the token
        token = social.utils.auth.genToken(user)
        current_app.logger.info("Gen a new token for %s - %s" % (user.username, token))

        # return token
        return utils.ok({
            "id": user.id,
            "token": token,
            "timestamp": int(time.time()),
        })