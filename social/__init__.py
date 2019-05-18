from flask import Flask, request, g, current_app, make_response, Blueprint
import os, time, datetime

from social import model, exception, utils, api
from social.api import *

from werkzeug.middleware.proxy_fix import ProxyFix
import simplejson

def create_app(config_filename = None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # debug the sql when development
    if app.config['DEBUG']:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # not using sqlalchemy event system, hence disabling it
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_filename is None:

        config = {
            "development": "social.config.DevelopmentConfig",
            "testing": "social.config.TestingConfig",
            "default": "social.config.ProductionConfig"
        }

        # load the instance config, if it exists, when not testing
        app.config.from_object(config[os.getenv('FLASK_ENV','default')])
        app.config.from_envvar('social_SETTING', silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(config_filename)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    model.db.init_app(app)
    utils.redis.init_app(app)

    app.register_blueprint(api.bp)

    # add Resource



    if not app.debug:
        @app.errorhandler(500)
        def serverInternalError(error):
            app.logger.exception("statucs code 500 %s : %s" % (request.remote_addr, error))
            return utils.fail("别说了，CrazyE被拿去下火锅去了", 500)


    @app.errorhandler(400)
    def serverInternalError(error):
        app.logger.warning("statucs code 400 %s : %s" % (request.remote_addr, error))
        return make_response(simplejson.dumps({
        "code":-1,
        "data":{},
        "msg": "你们啊，sometimes naive！"
    }   , separators=(',', ':'), sort_keys=True), 400)

    @app.errorhandler(404)
    def notFoundError(error):
        app.logger.warning("statucs code 404 %s : %s" % (request.remote_addr, error))
        return make_response(simplejson.dumps({
        "code":-1,
        "data":{},
        "msg": "你们啊，sometimes naive！"
    }, separators=(',', ':'), sort_keys=True), 404)

    @app.errorhandler(exception.InternalError)
    def serverInternalException(e):
        app.logger.exception(str(e))
        data = utils.fail(str(e), 500)
        return make_response(simplejson.dumps(data[0], separators=(',', ':'), sort_keys=True), data[1])


    @app.errorhandler(exception.NotFoundException)
    def serverNotfoundException(e):
        app.logger.exception(str(e))
        data = utils.fail(str(e), 404)
        return make_response(simplejson.dumps(data[0], separators=(',', ':'), sort_keys=True), data[1])

    @app.errorhandler(exception.LoginFailError)
    def LoginFailException(e):
        app.logger.exception(str(e))
        data = utils.fail(str(e), 401)
        return make_response(simplejson.dumps(data[0], separators=(',', ':'), sort_keys=True), data[1])


    @app.errorhandler(exception.DataInvaliError)
    def serverInternalException(e):
        app.logger.exception(str(e))
        data = utils.fail(str(e), 400)
        return make_response(simplejson.dumps(data[0], separators=(',', ':'), sort_keys=True), data[1])

    @app.teardown_request
    def checkin_db(exc):
        try:
            app.logger.info("Rollback the session")
            model.db.session.rollback()
        except AttributeError:
            pass

    return app