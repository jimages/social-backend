#!/usr/bin/python3
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, ValidationError, validates_schema, pre_load, post_load, post_dump, pre_dump
import re, datetime, json, time
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

class InstituteSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True, error_messages={'required': '缺少用户名.'})
    real_name = fields.Str(required=True, error_messages={'required': '缺少真实姓名.'})
    institute_id = fields.Integer(load_only=True,required=True, error_messages={'required': '缺少学院.'})
    institute = fields.Nested(InstituteSchema)
    password = fields.Str(load_only=True, required=True, error_messages={'required': "缺少密码"})

    @post_load
    def make_schedule(self, data):
        return model.User(**data)

class UserLoginSchema(Schema):
    username = fields.Str(required=True, error_messages={'required': '缺少用户名.'})
    password = fields.Str(load_only=True, required=True, error_messages={'required': "缺少密码"})

class PostSchema(Schema):
    id = fields.Integer(dump_only=True)

    body = fields.Str()
    uri = fields.Str()

    type = fields.Str(required=True)
    publish_type = fields.Str(required=True)

    user = fields.Nested(UserSchema)
    is_anonymous = fields.Boolean()
    anonymous_name = fields.Str()

    emoji1 = fields.Integer()
    emoji2 = fields.Integer()
    emoji3 = fields.Integer()
    emoji4 = fields.Integer()
    emoji5 = fields.Integer()

    @post_load
    def make(self, data):
        return model.Post(**data)
    # todo: 数据验证

class CommentSchema(Schema):
    id = fields.Integer()
    body = fields.Str()
    user = fields.Nested(UserSchema)

    is_anonymous = fields.Boolean()
    anonymous = fields.Str()