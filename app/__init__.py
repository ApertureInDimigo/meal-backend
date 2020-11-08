import firebase_admin
from firebase_admin import auth, storage
from firebase_admin import credentials
import os

from flask_admin import Admin
from flask import Flask, Response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from app.common.function import *
import json




class MyResponse(Response):
    default_mimetype = 'application/xml'

from flask import request, Response
from werkzeug.exceptions import HTTPException
import flask_admin.contrib.sqla


# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):

    import app.cache
    from app.scheduler import sched
    # from app.redis import redis_client
    import app.redis

    host_type = get_host_type()
    if host_type == "LOCAL":
        cred = credentials.Certificate("D:\Download\meal-project-fa430-firebase-adminsdk-st4ap-02bf8af80f.json")
        firebase = firebase_admin.initialize_app(cred)
    elif host_type == "VULTR":
        cred = credentials.Certificate("/var/yammeal/meal-project-fa430-firebase-adminsdk-st4ap-02bf8af80f.json")
        firebase = firebase_admin.initialize_app(cred)
    else:
        cred = json.loads(os.environ.get('FIREBASE_CONFIG', None))
        print(os.environ.get('FIREBASE_CONFIG', None))
        firebase = firebase_admin.initialize_app(credentials.Certificate(cred))









    app = Flask(__name__, static_url_path='', static_folder='../static', template_folder='../static')

    app.config.from_object(config_filename)
    # app.response_class = MyResponse

    from app.db import db, Student, School, MealRatingQuestion, MenuRating , MealBoardLikes, MealBoard
    db.init_app(app)
    db.app = app
    # sched.init_app(app)
    # redis_client.init_app(app)


    # Blueprints
    from app.auth.views import auth_bp
    from app.students.views import users_bp
    from app.schools.views import schools_bp
    from app.meals.views import meals_bp
    from app.board.views import board_bp
    from app.social.views import social_bp


    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/students')
    app.register_blueprint(schools_bp, url_prefix='/api/schools')
    app.register_blueprint(meals_bp, url_prefix='/api/meals')
    app.register_blueprint(board_bp, url_prefix='/api/board')
    app.register_blueprint(social_bp, url_prefix='/api/social')

    # sched.add_job(lambda: update_meal_board_views(), 'cron', second='05', id="update_meal_board_views")
    def update_meal_board_views():
        # from run import app
        with app.app_context():
            print("start!")
            post_seq_list = []
            view_count_list = []
            for key in rd.scan_iter(match="views:*"):
                post_seq_list.append(int(key.decode("utf-8").split("views:")[1]))
                view_count_list.append(len(rd.smembers(key)))
            print(post_seq_list)
            print(view_count_list)

            post_rows = MealBoard.query.filter(MealBoard.post_seq in post_seq_list).all()
            for index, post_row in enumerate(post_rows):
                post_row.views += view_count_list[index]
            db.session.commit()

    # if not get_host_type():
    #
    #     # set optional bootswatch theme
    #     app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    #
    #     admin = Admin(app, name='microblog', template_mode='bootstrap3')
    #     # Add administrative views here
    #
    #
    #
    #     class ModelView(flask_admin.contrib.sqla.ModelView):
    #         def is_accessible(self):
    #             auth = request.authorization or request.environ.get('REMOTE_USER')  # workaround for Apache
    #             if not auth or (auth.username, auth.password) != (app.config['ADMIN_ID'], app.config['ADMIN_PW']):
    #                 raise HTTPException('', Response(
    #                     "Please log in.", 401,
    #                     {'WWW-Authenticate': 'Basic realm="Login Required"'}
    #                 ))
    #             return True
    #
    #     admin.add_view(ModelView(Student, db.session))
    #     admin.add_view(ModelView(School, db.session))
    #     admin.add_view(ModelView(MenuRating, db.session))
    #     admin.add_view(ModelView(MealBoard, db.session))
    #     admin.add_view(ModelView(MealBoardLikes, db.session))
    #     admin.add_view(ModelView(MealRatingQuestion, db.session))




    CORS(app)
    return app
