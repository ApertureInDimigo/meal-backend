from flask import Flask, Response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

class MyResponse(Response):
    default_mimetype = 'application/xml'


# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__, static_url_path='', static_folder='../static', template_folder='../static')

    app.config.from_object(config_filename)
    # app.response_class = MyResponse

    from app.students.models import db
    db.init_app(app)

    # Blueprints
    from app.auth.views import auth_bp
    from app.students.views import users_bp
    from app.schools.views import schools_bp


    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/students')
    app.register_blueprint(schools_bp, url_prefix='/api/schools')

    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "meal-backend"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)



    CORS(app)
    return app
