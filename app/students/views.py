from flask import Blueprint
from flask_restful import Api

from app.students.api.IdCheck import IdCheck
from app.students.api.IdHint import IdHint
from app.students.api.NicknameCheck import NicknameCheck
from app.students.api.PasswordReset import PasswordReset
from app.students.api.PasswordResetCheckCode import PasswordResetCheckCode
from app.students.api.PasswordResetCheckMail import PasswordResetCheckMail
from app.students.api.Students import Students

users_bp = Blueprint('students', __name__)

api = Api(users_bp)


api.add_resource(Students, '')

api.add_resource(IdCheck, '/check-duplicate/id/<string:id>', '/check-duplicate/id/')
api.add_resource(NicknameCheck, '/check-duplicate/nickname/<string:nickname>', '/check-duplicate/nickname/')


api.add_resource(PasswordResetCheckMail, "/password-reset/check-mail")
api.add_resource(PasswordResetCheckCode, "/password-reset/check-code")
api.add_resource(PasswordReset, "/password-reset")

api.add_resource(IdHint, "/id-hint")