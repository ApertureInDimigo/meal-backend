from flask_wtf import FlaskForm
from wtforms import *

from marshmallow import Schema, fields, pprint, validate
from app.common.validator import *

class MenuDateSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate", validate=date_validator)


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
    menus = fields.List(fields.Nested(MenuStarSchema), required=True)


class MonthDaySchema(Schema):
    month = fields.String(required=True, data_key="month")
    year = fields.String(required=True, data_key="year")




class MenuDateSeqSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")
    menu_seq = fields.Integer(required=True, data_key="menuSeq")


class RatingQuestionSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate", validate=date_validator)
    menu = fields.Nested(MenuQuestionSchema, required=True)
