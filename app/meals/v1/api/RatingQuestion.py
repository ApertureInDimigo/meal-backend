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


class RatingQuestion(Resource):
    @return_500_if_errors
    @login_required
    def get(self):
        student_id = g.user_id
        args = request.args
        print(args)

        try:
            args = MenuDateSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401
        lunch_meal_data = get_day_meal(school, args["menu_date"], target_time=args["menu_time"])

        if lunch_meal_data is None:
            return {"message": "급식이 존재하지 않습니다."}, 404

        question_dict = []

        for index, menu in enumerate(lunch_meal_data):
            category = get_menu_category_list(menu)
            question_rows = get_question_rows(menu)
            question_dict.append({
                "menuSeq": index,
                "menuName": menu,
                "category": category,
                "questions": [
                    {
                        "questionSeq": question_row["question_seq"],
                        "content": question_row["content"],
                        "options": question_row["options"]
                    }

                    for question_row in question_rows]})

        return {
            "data": question_dict
        }