#!/usr/bin/python3
# -*- coding: utf-8 -*-

import flask, enum

from sqlalchemy import func
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import enum, time, hashlib, base64

# Init
db = SQLAlchemy()

class TimestampMixin(object):
    """Common Mixin for all Model"""

    time_created = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    time_updated = db.Column(db.TIMESTAMP, server_onupdate=func.current_timestamp(), server_default=func.current_timestamp())


class Institute(db.Model, TimestampMixin):
    """User definition"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(60), nullable=False, index=True)


class User(db.Model, TimestampMixin):
    """User definition"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(60), nullable=False, unique=True)
    password = db.Column(db.BINARY(60), nullable=True)  # Save bcrypt
    real_name = db.Column(db.CHAR(30), nullable=True)
    institute_id = db.Column(db.Integer, db.ForeignKey(Institute.id), nullable=True)


    institute = db.relationship("Institute", backref="users")

    def checkPassword(self, password: str):
        """Check the password of certain user

        :param username: username
        :param password: password
        :return: None if the user doesn't exist or User object if correct False otherwise.
        """


        if self.password is None:
            return None

        if bcrypt.checkpw(password.encode(), self.password):
            return self
        else:
            current_app.logger.warning("密码错误： %s" % self.username)
            return False

    @staticmethod
    def getByUsername(username: str):
        user = User.query.filter_by(username=username).first()
        if not user:
            current_app.logger.warning("用户username不存在： %s" % username)
            return None
        return user

    @staticmethod
    def getById(id):
        user = User.query.get(id)
        if not user:
            current_app.logger.info("用户id不存在： %s" % id)
            return None
        return user