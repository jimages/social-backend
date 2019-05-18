#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import make_response, Blueprint
from flask_restful import Api
import simplejson

from .user import *
from .institute import *

bp = Blueprint("api", "api", url_prefix="/api/v1")

restful = Api()

# We should init restful after add resource
restful.init_app(bp)


# extends the restful
@restful.representation('application/json')
def output_json(data, code, headers=None):
    data = simplejson.dumps(data, separators=(',', ':'), sort_keys=True)
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


@restful.representation('application/xml')
def output_json(data, code, headers=None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp

restful.add_resource(Register, "/user/register", endpoint="userRegister")
restful.add_resource(Login, "/user", endpoint="userLogin")
restful.add_resource(Institute, "/user/institute", endpoint="institute")
