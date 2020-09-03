import marshmallow

from app.common.decorator import login_required
from app.common.function import *

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate

from app.meals.form import RatingStarSchema, MenuDateSchema
from app.students.form import *
from werkzeug import ImmutableMultiDict
from flask import request, g
import requests
import json

from datetime import datetime
from statistics import mean
import numpy as np
from collections import defaultdict


class _RatingStar(Resource):

    @login_required
    def get(self):
        student_id = g.user_id
        args = request.get_json()

        try:
            args = MenuDateSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify(student_id)

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=0) \
            .filter(MenuRating.star.isnot(None)).first()
        if old_rating_row is None:
            return {"message": "평가한 후에 별점을 볼 수 있습니다."}, 409

        rating_rows = MenuRating.query.filter_by(school=school, menu_date=str_to_date(args["menu_date"]),
                                                 banned=False).all()

        rating_data = defaultdict(list)


        anal_result = list()

        for rating_row in rating_rows:
            rating_data[rating_row.menu_seq].append(rating_row)

        for menu_seq in sorted(list(rating_data.keys())):
            rating_list = rating_data[menu_seq]

            anal_result.append({
                "menuSeq" : menu_seq,
                "menuName" : rating_list[0].menu_name,
                "averageStar" : mean([rating.star for rating in rating_list])
            })

        return {
            "data" : anal_result
        }

    @login_required
    def post(self):

        student_id = g.user_id
        args = request.get_json()
        try:

            args = RatingStarSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        print(args)
        student = Student.query.filter_by(id=student_id).first()
        school = student.school
        lunch_meal_data = get_day_meal(school, args["menu_date"])

        # if args["menuName"] not in lunch_meal_data:
        #     return {"message": "급식이 존재하지 않습니다."}, 404

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=0) \
            .filter(MenuRating.star.isnot(None)).first()
        if old_rating_row is not None:
            return {"message": "이미 평가했습니다."}, 409

        menus = args["menus"]

        rating_rows = []

        now = datetime.now()
        for index, menu in enumerate(menus):
            if menu["menu_name"] in lunch_meal_data:
                if 1 <= menu["star"] <= 5 and menu["menu_name"] == lunch_meal_data[index] and menu["menu_seq"] == index:
                    rating_row = MenuRating(
                        school=school,
                        student=student,
                        menu_seq=menu["menu_seq"],
                        menu_name=menu["menu_name"],
                        menu_date=str_to_date(args["menu_date"]),
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
    #
    #     print(str_to_date(args["menuDate"]))
    #
    #     rating_row = MenuRating.query.filter_by(school=school, student=student, menu_name=args["menuName"],
    #                                             menu_date=str_to_date(args["menuDate"])) \
    #         .filter(MenuRating.star.isnot(None)).first()
    #     if rating_row is not None:
    #         return {"message": "이미 평가한 메뉴입니다."}, 404
    #
    #     rating_row = MenuRating(
    #         school = school,
    #         student = student,
    #         menu_name= args["menuName"],
    #         menu_date = str_to_date(args["menuDate"]),
    #         star = args["star"],
    #         banned = False,
    #         rating_date = datetime.now()
    #     )
    #     db.session.add(rating_row)
    #     db.session.commit()
    #
    #
    #     return lunch_meal_data
