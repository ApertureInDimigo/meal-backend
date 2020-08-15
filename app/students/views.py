from flask import Blueprint
from flask_restful import Api
from app.students.api import Students, IdCheck, NicknameCheck

users_bp = Blueprint('students', __name__)

api = Api(users_bp)


api.add_resource(Students, '')

api.add_resource(IdCheck, '/check-duplicate/id/<string:id>', '/check-duplicate/id/')
api.add_resource(NicknameCheck, '/check-duplicate/nickname/<string:nickname>', '/check-duplicate/nickname/')