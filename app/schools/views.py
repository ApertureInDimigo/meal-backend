from flask import Blueprint
from flask_restful import Api
from app.schools.api import _Schools, _SchoolCode

schools_bp = Blueprint('schools', __name__)

api = Api(schools_bp)


api.add_resource(_Schools, '')
api.add_resource(_SchoolCode, '/code-verify/', '/code-verify/<string:school_id>')
