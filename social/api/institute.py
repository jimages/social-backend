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
    'Institute',
]

ins_schema = schemas.InstituteSchema(many=True)

class Institute(Resource):
    def get(self):
        ins = model.Institute.query.all()
        ins = ins_schema.dump(ins)
        return utils.ok(dict(institutes=ins.data))