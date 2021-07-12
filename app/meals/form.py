from flask_wtf import FlaskForm
from wtforms import *

from marshmallow import Schema, fields, pprint, validate
from app.common.validator import *

class MenuDateSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate", validate=date_validator)
    menu_time = fields.String(required=False, data_key="menuTime", missing="중식")



class QuestionSchema(Schema):
    question_seq = fields.Integer(required=True, data_key="questionSeq")
    answer = fields.Integer(required=True, data_key="answer")


class MenuStarSchema(Schema):
    menu_seq = fields.Integer(required=True, data_key="menuSeq")
    # menu_name = fields.String(required=False, data_key="menuName")
    star = fields.Integer(required=True, data_key="star")


class MenuQuestionSchema(Schema):
    menu_seq = fields.Integer(required=True, data_key="menuSeq")
    # menu_name = fields.String(required=False, data_key="menuName")
    questions = fields.List(fields.Nested(QuestionSchema), required=True)


class RatingStarSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate", validate=date_validator)
    menu_time = fields.String(required=False, data_key="menuTime", missing="중식")
    menus = fields.List(fields.Nested(MenuStarSchema), required=True)



class MonthDaySchema(Schema):
    month = fields.String(required=False, data_key="month")
    year = fields.String(required=False, data_key="year")

    start_date = fields.String(required=False, data_key="startDate")
    end_date = fields.String(required=False, data_key="endDate")

    menu_time = fields.String(required=False, data_key="menuTime", missing="중식")




class MenuDateSeqSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")
    menu_time = fields.String(required=False, data_key="menuTime", missing="중식")
    menu_seq = fields.Integer(required=True, data_key="menuSeq")

class MenuDateSeqNameSchema(Schema):
    menu_date = fields.String(required=False, data_key="menuDate")
    menu_time = fields.String(required=False, data_key="menuTime", missing="중식")
    menu_seq = fields.Integer(required=False, data_key="menuSeq")
    menu_name = fields.String(required=False, data_key="menuName")


class RatingQuestionSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate", validate=date_validator)
    menu_time = fields.String(required=False, data_key="menuTime", missing="중식")
    menu = fields.Nested(MenuQuestionSchema, required=True)
