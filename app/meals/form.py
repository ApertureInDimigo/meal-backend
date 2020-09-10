from flask_wtf import FlaskForm
from wtforms import *

from marshmallow import Schema, fields, pprint, validate


class MenuDateSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")


class QuestionSchema(Schema):
    question_seq = fields.Integer(required=True, data_key="questionSeq")
    answer = fields.Integer(required=True, data_key="answer")


class MenuStarSchema(Schema):
    menu_seq = fields.Integer(required=True, data_key="menuSeq")
    menu_name = fields.String(required=False, data_key="menuName")
    star = fields.Integer(required=True, data_key="star")


class MenuQuestionSchema(Schema):
    menu_seq = fields.Integer(required=True, data_key="menuSeq")
    # menu_name = fields.String(required=False, data_key="menuName")
    questions = fields.List(fields.Nested(QuestionSchema), required=True)


class RatingStarSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")
    menus = fields.List(fields.Nested(MenuStarSchema), required=True)


class MenuDateSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")


class MenuDateSeqSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")
    menu_seq = fields.Integer(required=True, data_key="menuSeq")


class RatingQuestionSchema(Schema):
    menu_date = fields.String(required=True, data_key="menuDate")
    menu = fields.Nested(MenuQuestionSchema, required=True)
