#!/usr/bin/python3
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, ValidationError, validates_schema, pre_load, post_load, post_dump, pre_dump
import re, datetime, json
from social import model
from bcrypt import gensalt, hashpw
from flask import g

class ChineseCellphone(fields.Str):
    def _deserialize(self, value, attr, data):
        if not re.match(re.compile("^1[3-9][0-9]{9}$"), value):
            raise ValidationError("手机号码输入不正确")
        return value

class Enum(fields.Field):
    def _serialize(self, value, attr, data):
        if isinstance(value, Enum):
            raise ValidationError("not Enum type")
        return value.value

class Timestamp(fields.Field):
    def _serialize(self, value, attr, data):
        if isinstance(value, datetime.datetime):
            return int(value.timestamp())
        if isinstance(value, datetime.date):
            timestamp = time.mktime(value.timetuple())
            return int(timestamp)
        elif value is None:
            return None
        else:
            raise ValidationError("not valid type")


    def _deserialize(self, value, attr, data):
        if isinstance(value, int):
            ValidationError("not int type")
            return datetime.datetime.fromtimestamp(value)
        elif value is None:
            return None
        else:
            raise ValidationError("not valid type")


class Sha256(fields.Str):
    def _deserialize(self, value, attr, data):
        if not re.match(re.compile("^[A-Fa-f0-9]{64}$"), value):
            raise ValidationError("你的签名似乎有问题？你想搞个大新闻？")
        return value

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True, error_messages={'required': '缺少用户名.'})
    real_name = fields.Str(required=True, error_messages={'required': '缺少真实姓名.'})
    institute = fields.Str(required=True, error_messages={'required': '缺少学院.'})
    password = fields.Str(load_only=True, required=True, error_messages={'required': "缺少密码"})

    @post_load
    def make_schedule(self, data):
        return model.User(**data)

class UserLoginSchema(Schema):
    username = fields.Str(required=True, error_messages={'required': '缺少用户名.'})
    password = fields.Str(load_only=True, required=True, error_messages={'required': "缺少密码"})
