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


class RatingStar(Resource):
    @return_500_if_errors
    @login_required
    def get(self):

        """
        평균 별점 결과 확인 (당일이라면 자신이 평가한 메뉴만 보여주고, 과거의 급식이라면 모두 보여줌)
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

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        if is_same_date(datetime.now(), str_to_date(args["menu_date"])):

            old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                        menu_date=str_to_date(args["menu_date"]),
                                                        menu_time=args["menu_time"]) \
                .filter(MenuRating.star.isnot(None)).all()

            # if old_rating_row is None:
            #     return {"message": "평가한 후에 별점을 볼 수 있습니다."}, 409

            old_rating_menu_seq_list = [rating_row.menu_seq for rating_row in old_rating_row]

            rating_rows = MenuRating.query.filter_by(school=school, menu_date=str_to_date(args["menu_date"]),
                                                     menu_time=args["menu_time"],
                                                     banned=False).filter(MenuRating.star.isnot(None)).filter(
                MenuRating.menu_seq.in_(old_rating_menu_seq_list)).all()

        else:
            rating_rows = MenuRating.query.filter_by(school=school, menu_date=str_to_date(args["menu_date"]),
                                                     menu_time=args["menu_time"],
                                                     banned=False).filter(MenuRating.star.isnot(None)).all()

        rating_data = defaultdict(list)

        anal_result = list()

        for rating_row in rating_rows:
            rating_data[rating_row.menu_seq].append(rating_row)

        for menu_seq in sorted(list(rating_data.keys())):
            rating_list = rating_data[menu_seq]

            anal_result.append({
                "menuSeq": menu_seq,
                "menuName": rating_list[0].menu_name,
                "averageStar": mean([rating.star for rating in rating_list])
            })

        return {
            "data": anal_result
        }

    @return_500_if_errors
    @login_required
    def post(self):
        """
        급식 메뉴에 대해 별점 추가
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        404 : 해당 급식이 없음
        406 : 급식 날짜 당일이 아님
        409 : 이미 평가함
        """
        student_id = g.user_id
        args = request.get_json()
        try:

            args = RatingStarSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        print(args)

        if not is_same_date(str_to_date(args["menu_date"]), datetime.now()):
            return {"message": "당일에만 평가할 수 있습니다."}, 406

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        lunch_meal_data = get_day_meal(school, args["menu_date"], target_time=args["menu_time"])

        # if args["menuName"] not in lunch_meal_data:
        #     return {"message": "급식이 존재하지 않습니다."}, 404

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]),
                                                    menu_time=args["menu_time"]) \
            .filter(MenuRating.star.isnot(None)).all()

        old_rating_menu_seq_list = [rating_row.menu_seq for rating_row in old_rating_row]

        # if old_rating_row is not None:
        #     return {"message": "이미 평가했습니다."}, 409

        menus = args["menus"]

        rating_rows = []

        now = datetime.now()
        for index, menu in enumerate(menus):
            if 0 <= menu["menu_seq"] <= len(lunch_meal_data) - 1:
                if 1 <= menu["star"] <= 5:

                    if menu["menu_seq"] in old_rating_menu_seq_list:
                        continue

                    rating_row = MenuRating(
                        school=school,
                        student=student,
                        menu_seq=menu["menu_seq"],
                        menu_name=lunch_meal_data[menu["menu_seq"]],
                        menu_date=str_to_date(args["menu_date"]),
                        menu_time=args["menu_time"],
                        star=menu["star"],
                        banned=False,
                        rating_date=now
                    )
                    rating_rows.append(rating_row)
                else:
                    return {"message": "파라미터 값이 올바르지 않습니다."}, 400
            else:
                return {"message": "급식이 존재하지 않습니다."}, 404

        print(rating_rows)
        db.session.add_all(
            rating_rows
        )
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200