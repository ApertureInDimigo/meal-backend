from flask_wtf import FlaskForm
from wtforms import *

from marshmallow import Schema, fields, pprint, validate


class StudentSchema(Schema):
    # id = fields.String(required=True, validate=validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,15}$'))
    id = fields.String(required=True, validate=validate.Regexp(
        r'^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$'))
    password = fields.String(required=True, validate=validate.Regexp(
        r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&-_])[A-Za-z\d$@$!%*#?&-_]{6,15}$'))
    nickname = fields.String(required=True, validate=validate.Regexp(r'^[가-힣0-9A-Za-z]{2,10}$'))
    school_grade = fields.Integer(required=True, data_key="schoolGrade")
    school_class = fields.Integer(required=True, data_key="schoolClass")
    school_id = fields.Integer(required=True, data_key="schoolId")
    school_code = fields.String(required=False, data_key="schoolCode")

    access_token = fields.String(required=False, data_key="accessToken")

class EmailSchema(Schema):
    # id = fields.String(required=True, validate=validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,15}$'))
    id = fields.String(required=True, validate=validate.Regexp(
        r'^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$'))

class EmailCodeSchema(Schema):
    # id = fields.String(required=True, validate=validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,15}$'))
    id = fields.String(required=True, validate=validate.Regexp(
        r'^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$'))
    code = fields.Integer(required=True)


class PasswordSchema(Schema):
    password = fields.String(required=True, validate=validate.Regexp(
        r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&-_])[A-Za-z\d$@$!%*#?&-_]{6,15}$'))


class NicknameSchema(Schema):

    nickname = fields.String(required=True, validate=validate.Regexp(r'^[가-힣0-9A-Za-z]{2,10}$'))