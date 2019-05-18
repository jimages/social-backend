import json
import os
from flask import current_app

import time, bcrypt
from flask import request, current_app, g, abort
from flask_restful import Resource
from social import model, schemas, exception, utils
from social.utils import authRequired
from sqlalchemy import or_, and_
__all__ = [
    'Post',
    'Upvote',
    "Comment"
]

post_schema = schemas.PostSchema()
posts_schema = schemas.PostSchema(many=True)
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

    @authRequired
    def get(self):
        after = request.args.get('after' ,None ,int)
        type = request.args.get('type', 'all', str)

        if type == 'all' and after is None:
            # 这里的所有表示的是又包括自己的学校还有自己的学院
            posts = model.Post.query.filter(or_(and_(model.Post.publish_type == 'institute', model.Post.publish_id == g.current_user.institute_id),
                model.Post.publish_type == 'all')).order_by(model.Post.id.desc()).limit(30).all()

        elif type == 'all' and after is not None:
            posts = model.Post.query.filter(or_(and_(model.Post.publish_type == 'institute', model.Post.publish_id == g.current_user.institute_id),
                model.Post.publish_type == 'all')).filter(model.Post.id < after).order_by(model.Post.id.desc()).limit(30).all()
        elif type == "institute" and after is None:
            posts = model.Post.query.filter(and_(model.Post.publish_type == 'institute', model.Post.publish_id == g.current_user.institute_id)).order_by(model.Post.id.desc()).limit(30).all()

        elif type == "institute" and after is not None:
            posts = model.Post.query.filter(and_(model.Post.publish_type == 'self', model.Post.publish_id == g.current_user.institute_id)).filter(model.Post.id < after).order_by(model.Post.id.desc()).limit(30).all()

        elif after is not None:
            posts = model.Post.query.filter(and_(model.Post.publish_type == 'self', model.Post.publish_id == g.current_user.id)).order_by(model.Post.id.desc()).limit(30).all()
        else:
            posts = model.Post.query.filter(and_(model.Post.publish_type == 'self', model.Post.publish_id == g.current_user.id, model.Post.id < after)).order_by(model.Post.id.desc()).limit(30).all()

        posts = posts_schema.dump(posts)

        return utils.ok(posts.data)


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

        json = request.get_json()

        comment = comment_schema.load(json)
        post = model.Post.query.get(json['post_id'])
        if post is None:
            raise exception.DataInvaliError("not found post")
        comment.data.post_id = post.id
        comment.data.user_id = g.current_user.id

        model.db.session.add(comment.data)
        model.db.session.commit()

        comment = comment_schema.dump(comment.data)
        return utils.ok(comment.data, 201)