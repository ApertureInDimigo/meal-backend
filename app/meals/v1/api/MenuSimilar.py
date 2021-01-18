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

class MenuSimilar(Resource):
    @return_500_if_errors
    @login_required
    def get(self):

        student_id = g.user_id
        args = request.args
        print(args)

        try:
            args = MenuDateSeqSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        print(args)
        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        day_meal_data = get_day_meal(school, args["menu_date"], target_time=args["menu_time"])
        if day_meal_data is None:
            return {"message": "급식이 존재하지 않습니다."}, 404
        try:
            target_menu = day_meal_data[args["menu_seq"]]
        except (IndexError, ValueError):
            return {"message": "급식이 존재하지 않습니다."}, 404

        end_date = str_to_date(args["menu_date"]) - timedelta(days=1)
        start_date = str_to_date(args["menu_date"]) - timedelta(days=91)

        range_meal_data = get_range_meal(school, start_date=date_to_str(start_date), end_date=date_to_str(end_date),
                                         target_time="전체")

        result = []

        for date in range_meal_data:
            for time, menus in range_meal_data[date].items():
                for menu in menus:
                    if menu == target_menu:

                        result.append({
                            "menuDate": date, "menuTime": time, "menu": menu, "distance" : 0, "menuSeq" : menus.index(menu)
                        })
                    else:
                        distance = edit_distance(target_menu, menu)
                        if distance <=  max(len(menu),len(target_menu)) // 1.5:
                            result.append({
                                "menuDate": date, "menuTime": time, "menu": menu, "distance": distance, "menuSeq" : menus.index(menu)
                            })


        # print(range_meal_data)

        result = sorted(result, key=lambda x : int(x["menuDate"]), reverse=True)

        return {
            "data":{
                "target" : target_menu,
                "menus" :  result
            }
        }