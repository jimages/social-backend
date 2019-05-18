import hashlib, hmac
import uuid

from flask import request, current_app, g

from social import model
from social.utils.redis import redis
from social.exception import AuthFailError


def genToken(user :object, expiration = 30 * 24 * 3600):
    """Generate a token and save it to redis server
    :param expiration: TTL
    :param salt: username
    :type salt: str
    :type expiration: int
    :return:
    """
    token = uuid.uuid4()

    redis.set("login+" + user.name, token.hex, expiration)

    return token.hex


def getToken(user: object):
    """Check the token

    :param token: token
    :return: User object if success, None otherwise
    """
    result = redis.get("login+" + user.name)

    # extend the ttl
    if result is not None:
        redis.expire("login" + user.name, 30 * 24 * 3600)

    return None if result is None else result.decode()


def freshToken(user: object, exp: int = 30 * 24 * 3600):
    """Fresh the TTL of certain token

    :param username: token to fresh
    :param exp: TTL
    :return: True if success, False otherwise
    """
    re = redis.expire("login+" + user.name, exp)

    return True if re == True else None


def authRequired(func):
    def wrapper(*args, **kwargs):
        try:
            id = request.headers.get('user-id', None)
            sign = request.headers.get('digest', None)
            timestamp = request.headers.get('timestamp', None)

            if id is None or sign is None or timestamp is None:
                current_app.logger.warn("缺少digest或id或者timestamp：%s", request.remote_addr)
                raise AuthFailError

            user = model.User.getById(id)
            if user is None:
                current_app.logger.warn("user不存在：%s", request.remote_addr)
                raise AuthFailError
            else:
                # Now we check the sign
                token = getToken(user)
                current_app.logger.info("We now get token %s" % token)
                if token is None:
                    current_app.logger.warn("user对应token不存在：%s %s", id, request.remote_addr)
                    raise AuthFailError

                data = {**request.args.to_dict(), **request.form.to_dict()}

                uri = request.path
                s = genSign(uri, data, timestamp , current_app.config["APP_KEY"], token)

                if s != sign:
                    current_app.logger.warn("认证失败: %s", request.remote_addr)
                    if not current_app.debug:
                        # in debug mode we skip the authorized stop
                        raise AuthFailError

                g.current_user = user

        except AuthFailError:
            current_app.logger.warn("api鉴权失败 ip: %s", request.remote_addr)
            # We can't use the flask error handler for some reason, We will check later.
            return  ({"code":-1, "body":None, "msg":"你要搞个大新闻？"}, 401)
        else:
            return func(*args, **kwargs)
    return wrapper


def genSign(uri, dict, timestamp, app_token : str, user_token : str = str()):
    """Generate a signature of the post code

    :param dict: the form or get query
    :param app_token: the token we need sign
    :param user_token: token of user
    :type dict dict
    :type app_token str
    :type user_token str

    :return: the sign string
    """

    strings = []
    for key, value in sorted(dict.items()):
        strings.append("%s=%s" % (key, value))
    secret = user_token + app_token
    msg =  "+".join([timestamp, uri, "&".join(strings)])
    current_app.logger.debug("the message is %s", msg)

    digest = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
    current_app.logger.debug("the digest is %s", digest)

    return digest

