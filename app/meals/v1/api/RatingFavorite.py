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


class RatingFavorite(Resource):
    @return_500_if_errors
    @login_required
    def get(self):

        """
        즐겨찾기한 메뉴를 봄.
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        404 : 즐겨찾기가 없음
        """

        student_id = g.user_id
        args = request.args
        print(args)
        try:
            args = MonthDaySchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        rating_rows = db.session.query().with_entities(MenuRating.menu_name).filter_by(school=school,
                                                                                       student=student).filter(
            MenuRating.is_favorite.isnot(None)).all()
        favorite_name_list = [rating_row.menu_name for rating_row in rating_rows]
        # return

        if "year" in args and "month" in args:
            lunch_meal_list_data = get_month_meal(school, args["year"], args["month"], target_time=args["menu_time"])
        elif args["start_date"] is not None and args["end_date"] is not None:
            lunch_meal_list_data = get_range_meal(school, args["start_date"], args["end_date"],
                                                  target_time=args["menu_time"])
        print(lunch_meal_list_data)
        print(favorite_name_list)

        favorite_dict = defaultdict(list)

        for date, menus in lunch_meal_list_data.items():
            for menu in menus:
                if menu in favorite_name_list:
                    favorite_dict[date].append(menu)

        if len(favorite_dict) == 0:
            return {
                       "message": "즐겨찾기가 없습니다."
                   }, 404

        return {
                   "data": favorite_dict
               }, 200

    @return_500_if_errors
    @login_required
    def post(self):
        """
        즐겨찾기 메뉴 추가
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        404 : 즐겨찾기가 없음
        409 : 이미 좋아하는 메뉴임
        """

        student_id = g.user_id
        args = request.get_json()
        try:

            args = MenuDateSeqSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401
        lunch_meal_data = get_day_meal(school, args["menu_date"], target_time=args["menu_time"])

        # if args["menuName"] not in lunch_meal_data:
        #     return {"message": "급식이 존재하지 않습니다."}, 404

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=args["menu_seq"]) \
            .filter(MenuRating.is_favorite.isnot(None)).first()
        if old_rating_row is not None:
            return {"message": "이미 좋아하는 메뉴입니다."}, 409

        # print(args["menu_seq"], len(lunch_meal_data))
        now = datetime.now()
        if 0 <= args["menu_seq"] < len(lunch_meal_data):
            rating_row = MenuRating(
                school=school,
                student=student,
                menu_seq=args["menu_seq"],
                menu_name=lunch_meal_data[args["menu_seq"]],
                menu_date=str_to_date(args["menu_date"]),
                is_favorite=True,
                banned=False,
                rating_date=now
            )

            db.session.add(rating_row)
            db.session.commit()

        else:
            return {"message": "메뉴가 존재하지 않습니다."}, 404

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200

    @return_500_if_errors
    @login_required
    def delete(self):

        """
        즐겨찾기한 메뉴 삭제.
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        409 : 즐겨찾기 한 메뉴가 아님.
        """

        student_id = g.user_id
        args = request.args
        try:

            args = MenuDateSeqNameSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        if "menu_name" in args and args["menu_name"] is not None:
            old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                        menu_name=args["menu_name"]) \
                .filter(MenuRating.is_favorite.isnot(None)).all()
        else:
            lunch_meal_data = get_day_meal(school, args["menu_date"], target_time=args["menu_time"])
            if lunch_meal_data is None:
                return {"message": "파라미터 값이 유효하지 않습니다."}, 400

            # if args["menuName"] not in lunch_meal_data:
            #     return {"message": "급식이 존재하지 않습니다."}, 404

            old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                        menu_name=lunch_meal_data[args["menu_seq"]]) \
                .filter(MenuRating.is_favorite.isnot(None)).all()
        if old_rating_row is None:
            return {"message": "좋아하지 않는 메뉴입니다."}, 409

        for rating_row in old_rating_row:
            db.session.delete(rating_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200