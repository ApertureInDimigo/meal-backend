import firebase_admin
from firebase_admin import auth, storage
from firebase_admin import credentials
import os


from flask import Flask, Response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from app.common.function import *
import json
class MyResponse(Response):
    default_mimetype = 'application/xml'


# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):

    if is_local() is True:
        cred = credentials.Certificate("D:\Download\meal-project-fa430-firebase-adminsdk-st4ap-02bf8af80f.json")
        firebase = firebase_admin.initialize_app(cred)
    else:
        cred = json.loads(os.environ.get('FIREBASE_CONFIG', None))
        print(os.environ.get('FIREBASE_CONFIG', None))
        firebase = firebase_admin.initialize_app(cred)








    app = Flask(__name__, static_url_path='', static_folder='../static', template_folder='../static')

    app.config.from_object(config_filename)
    # app.response_class = MyResponse

    from app.students.models import db
    db.init_app(app)

    # Blueprints
    from app.auth.views import auth_bp
    from app.students.views import users_bp
    from app.schools.views import schools_bp
    from app.meals.views import meals_bp
    from app.board.views import board_bp


    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/students')
    app.register_blueprint(schools_bp, url_prefix='/api/schools')
    app.register_blueprint(meals_bp, url_prefix='/api/meals')
    app.register_blueprint(board_bp, url_prefix='/api/board')


    CORS(app)
    return app
