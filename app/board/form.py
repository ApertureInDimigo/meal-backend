from flask_wtf import FlaskForm
from wtforms import *

from marshmallow import Schema, fields, pprint, validate

class MealBoardSchema(Schema):
    # id = fields.String(required=True, validate=validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,15}$'))
    menu_date = fields.String(required=True, data_key="menuDate")

    title = fields.String(required=True, data_key="title")
    content = fields.String(required=True, data_key="content")


class MealBoardGetListSchema(Schema):

    page = fields.Integer(required=True, validate=validate.Range(min=0, max=999))
    limit = fields.Integer(required=True ,validate=validate.Range(min=0, max=30))