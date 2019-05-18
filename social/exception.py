#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import current_app

class SocialException(Exception):
    """Base exception for timetable"""
    pass


class DataInvaliError(SocialException):
    pass


class AuthFailError(SocialException):
    pass


class LoginFailError(SocialException):
    pass


class InternalError(SocialException):
    pass


class Unauthorized(SocialException):
    pass

class NotFoundException(SocialException):
    pass