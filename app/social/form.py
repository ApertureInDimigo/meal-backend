from flask_wtf import FlaskForm
from wtforms import *

from marshmallow import Schema, fields, pprint, validate
from app.common.validator import *



class SocialSearchQuerySchema(Schema):
    query = fields.String(required=True, data_key="query")
    type = fields.String(required=False, data_key="type")