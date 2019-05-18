import json

class Config(object):
    DEBUG = False
    TESTING = False
    POST_TYPES = ['text', 'url']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = "a2489329308d463babce9c67a01a8242"
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://root@localhost/social?charset=utf8mb4"
    SQLALCHEMY_POOL_RECYCLE = 60
    REDIS_URL = "redis://localhost/0"
    UPLOAD_FOLDER = "/var/www/html/img"


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///memory"
    TESTING = True