import marshmallow

from app.common.decorator import login_required, return_500_if_errors
from app.common.function import *

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate

from app.meals.form import RatingStarSchema, MenuDateSchema, RatingQuestionSchema, \
    MenuDateSeqSchema, MonthDaySchema, MenuDateSeqNameSchema
from app.students.form import *

from flask import request, g
import requests
import json

from datetime import datetime, timedelta
from statistics import mean
import numpy as np
from collections import defaultdict
from sqlalchemy import extract

from config import SECRET_KEY
from sample.menu_classifier import classify_menu

class UpdateMealQuestion(Resource):

    def get(self):
        if request.args.get("key", None) != SECRET_KEY:
            return "error"

        len_data = fetch_spread_sheet()
        return f"success! {len_data}"
