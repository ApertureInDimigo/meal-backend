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

class Menu(Resource):
    @return_500_if_errors
    @login_required
    def get(self):
        """
        메뉴 보여줌
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        """

        student_id = g.user_id
        args = request.args
        print(args)

        try:
            args = MenuDateSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        print(args)
        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        lunch_meal_data = get_day_meal(school, args["menu_date"], target_time=args["menu_time"])
        # lunch_meal_data = get_range_meal(school, start_date="20201001", end_date="20201115", target_time=args["menu_time"])
        return {
            "data": lunch_meal_data
        }
