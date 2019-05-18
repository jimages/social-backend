import json
import os
from flask import current_app

import time, bcrypt
from flask import request, current_app, g, abort
from flask_restful import Resource
from social import model, schemas, exception, utils
from social.utils import authRequired

__all__ = [
    'Post',
    'Upvote'
]

post_schema = schemas.PostSchema()
comment_schema = schemas.CommentSchema()

class Post(Resource):
    """分享"""
    @authRequired
    def post(self):
        current_app.logger.info("Create Post")

        json = request.get_json()
        if json is None:
            abort(400)

        data = post_schema.load(json)

        if data.errors:
            raise exception.DataInvaliError("数据错误")

        data = data.data

        data.user_id = g.current_user.id

        if data.publish_type == "institute":
            data.publish_id = g.current_user.institute_id
        elif data.publish_type == "self":
            data.publish_id = g.current_user.id

        model.db.session.add(data)
        model.db.session.commit()

        data = post_schema.dump(data)
        if data.errors:
            raise exception.DataInvaliError("数据错误")

        return utils.ok(data.data, 201)

class Upvote(Resource):
    @authRequired
    def post(self):
        current_app.logger.info("Upvote")

        json = request.get_json()

        # todo 检查
        post_id = json['post_id']
        upvote = json['upvote']

        post = model.Post.query.get(post_id)
        if post is None:
            raise exception.DataInvaliError("invalid data")

        setattr(post, upvote, getattr(post, upvote) + 1)
        model.db.session.add(post)
        model.db.session.commit()

        post = post_schema.dump(post)
        return post.data, 201

class Comment(Resource):
    @authRequired
    def post(self):
        current_app.logger.info("Comment")

