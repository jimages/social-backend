from flask import Flask, request, g, current_app, make_response
import os, time, datetime

from social import model, exceptions, utils

from werkzeug.contrib.fixers import ProxyFix
import flask_restful, simplejson

restful = flask_restful.Api()


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
            "development": "timetable.config.DevelopmentConfig",
            "testing": "timetable.config.TestingConfig",
            "default": "timetable.config.ProductionConfig"
        }

        # load the instance config, if it exists, when not testing
        app.config.from_object(config[os.getenv('FLASK_ENV','default')])
        app.config.from_envvar('TIMETABLE_SETTING', silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(config_filename)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    if not app.testing:
        redis.init_app(app)
        rabbitmq.init_app(app)
        model.mongo.init_app(app, **app.config['MONGO_PARAMS'])
    model.db.init_app(app)

    # add Resource
    restful.add_resource(UserTel, "/v2/users", endpoint="tel_user_login")
    restful.add_resource(RegisterPush, "/v2/users/push", endpoint="register_push")
    restful.add_resource(University, "/v2/universities", endpoint="university_list")
    restful.add_resource(EducationAccount, "/v2/universities/accounts", endpoint="education_account")
    restful.add_resource(Refresh, "/v2/universities/accounts/refresh", endpoint="refresh_account")
    restful.add_resource(Today, "/v2/universities/today", endpoint="current_semester")
    restful.add_resource(TimeSchedule, "/v2/universities/schedules", endpoint="schedule")
    restful.add_resource(Course, "/v2/courses", "/v2/courses/<string:semester>", endpoint="course_list")
    restful.add_resource(Grade, "/v2/grades", endpoint="grade_list")
    restful.add_resource(Exam, "/v2/exams", endpoint="exam_list")
    restful.add_resource(NoteList, "/v2/notes", endpoint="notelist")
    restful.add_resource(NoteOperation, "/v2/notes/<int:id>", endpoint="noteoperation")

    # about File
    restful.add_resource(File, "/v2/files", "/v2/files/<int:id>", endpoint="file")
    restful.add_resource(FileCheck, "/v2/filesCheck", endpoint="fileCheck")
    restful.add_resource(DownloadFile, "/v2/fileDownload/<int:file_id>")
    restful.add_resource(DownloadRecords, "/v2/downloadRecords")

    # shares
    restful.add_resource(DocumentFrontApi, "/v2/functions/documents")
    restful.add_resource(Shares, "/v2/shares")
    restful.add_resource(Search, "/v2/search")
    restful.add_resource(Upvote, "/v2/shares/upvotes")
    restful.add_resource(CertainShare, "/v2/shares/<int:share_id>")
    restful.add_resource(UserShare, "/v2/shares/my")
    restful.add_resource(Comment, "/v2/comments")
    restful.add_resource(SubComment, "/v2/subcomments")
    restful.add_resource(Category, "/v2/categories")
    restful.add_resource(RecommentCategory, "/v2/categories/recommend")

    # config
    restful.add_resource(Config, "/v2/config")

    # Hotpot
    restful.add_resource(Transaction, "/v2/hotpot/transactions")
    restful.add_resource(Price, "/v2/hotpot/prices")
    restful.add_resource(Topup, "/v2/hotpot")
    restful.add_resource(TopupForIap, "/v2/hotpot/iap")
    restful.add_resource(TopupForAlipay, "/v2/hotpot/alipay")
    restful.add_resource(TopupForWechat, "/v2/hotpot/wechat")

    # Pay
    restful.add_resource(PrepareTopupForAlipay, "/v2/pay/alipay")
    restful.add_resource(PrepareTopupForWechat, "/v2/pay/wechat")

    # Abuse
    restful.add_resource(AbuseList, "/v2/abuse_list")
    restful.add_resource(Abuse, "/v2/abuse")




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

    @app.errorhandler(exceptions.InternalError)
    def serverInternalException(e):
        app.logger.exception(str(e))
        data = utils.fail(str(e), 500)
        return make_response(simplejson.dumps(data[0], separators=(',', ':'), sort_keys=True), data[1])


    @app.errorhandler(exceptions.NotFoundException)
    def serverNotfoundException(e):
        app.logger.exception(str(e))
        data = utils.fail(str(e), 404)
        return make_response(simplejson.dumps(data[0], separators=(',', ':'), sort_keys=True), data[1])


    @app.errorhandler(exceptions.DataInvaliError)
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
    @app.before_request
    def set_start_time():
        g.start_time = time.time()

        today = datetime.datetime.today()
        today = "-".join([str(today.year), str(today.month), str(today.day)])
        g.info_today = today
        redis.incr("info:apicount:" + today)
    @app.after_request
    def get_average_responce_time(res):
        count = int(redis.get("info:apicount:" + g.info_today))
        average_time = redis.get("info:apicount_average_process:" + g.info_today)
        time_last = (time.time() - g.start_time) * 1000
        current_app.logger.info("Process time %s" % time_last)
        if average_time is None:
            average_time = time_last
        else:
            average_time = (float(average_time) * (count - 1) + time_last) / count
        redis.set("info:apicount_average_process:" + g.info_today, average_time, 3600 * 24 * 30)
        return res

    # We should init restful after add resource
    restful.init_app(app)

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

    return app