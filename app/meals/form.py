from flask_wtf import FlaskForm
from wtforms import *

from marshmallow import Schema, fields, pprint, validate



class MenuDateSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")




class MenuSchema(Schema):

    menu_seq = fields.Integer(required=True, data_key="menuSeq")
    menu_name = fields.String(required=False, data_key="menuName")
    star = fields.Integer(required=False, data_key="star")




class RatingStarSchema(Schema):


    menu_date = fields.String(required=True, data_key="menuDate")
    menus = fields.List(fields.Nested(MenuSchema))


    #
    # # id = fields.String(required=True, validate=validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,15}$'))
    # id = fields.String(required=True, validate=validate.Regexp(
    #     r'^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$'))
    # password = fields.String(required=True, validate=validate.Regexp(
    #     r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&-_])[A-Za-z\d$@$!%*#?&-_]{6,15}$'))
    # nickname = fields.String(required=True, validate=validate.Regexp(r'^[가-힣0-9A-Za-z]{2,10}$'))
    # school_grade = fields.Integer(required=True, data_key="schoolGrade")
    # school_class = fields.Integer(required=True, data_key="schoolClass")
    # school_id = fields.Integer(required=True, data_key="schoolId")
    # school_code = fields.String(required=False, data_key="schoolCode")
    #
    # access_token = fields.String(required=False, data_key="accessToken")