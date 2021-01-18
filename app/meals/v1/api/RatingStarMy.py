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


class RatingStarMy(Resource):

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

        rating_rows = MenuRating.query.filter_by(student=student, school=school, banned=False,
                                                 menu_date=str_to_date(args["menu_date"]),
                                                 menu_time=args["menu_time"]).filter(
            MenuRating.star.isnot(None)).all()
        if rating_rows is None:
            return {"message": "평가한 메뉴가 없습니다."}, 404

        rating_result = []
        for rating_row in rating_rows:
            rating_result.append({
                "menuSeq": rating_row.menu_seq,
                "menuName": rating_row.menu_name,
                "star": rating_row.star
            })

        return {
            "data": rating_result
        }