import marshmallow

from app.common.decorator import login_required
from app.common.function import *

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate
from app.students.form import *
from werkzeug import ImmutableMultiDict
from flask import request, g
import requests
import json

from datetime import datetime


class _RatingStar(Resource):
    def get(self):
        pass

    @login_required
    def post(self):
        student_id = g.user_id
        args = request.get_json()
        if args is None:
            return {"message": "파라미터 값이 올바르지 않습니다."}, 400
        if args["star"] is None or type(args["star"]) != int or not (1 <= args["star"] <= 5):
            return {"message": "파라미터 값이 올바르지 않습니다."}, 400
        if args["menuName"] is None or type(args["menuName"]) != str or args["menuDate"] is None or type(
                args["menuDate"]) != str:
            return {"message": "파라미터 값이 올바르지 않습니다."}, 400
        student = Student.query.filter_by(id=student_id).first()
        school = student.school
        school_id, school_region = school.school_id, school.region

        print(school_id)

        url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={get_region_code(school_region)}&SD_SCHUL_CODE={school_id}&MLSV_FROM_YMD={args['menuDate']}&MLSV_TO_YMD={args['menuDate']}&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a&pSize=365&Type=json"

        meal_response = requests.request("GET", url)
        meal_data = json.loads(meal_response.text)
        if "mealServiceDietInfo" not in meal_data:
            return {"message": "급식이 존재하지 않습니다."}, 404
        day_meal_data = meal_data["mealServiceDietInfo"][1]["row"]

        lunch_meal_data = []
        for time_meal_data in day_meal_data:
            if time_meal_data["MMEAL_SC_NM"] == "중식":
                lunch_meal_data = [remove_allergy(menu) for menu in time_meal_data["DDISH_NM"].split("<br/>")]

        if len(lunch_meal_data) == 0:
            return {"message": "급식이 존재하지 않습니다."}, 404

        if args["menuName"] not in lunch_meal_data:
            return {"message": "급식이 존재하지 않습니다."}, 404

        print(str_to_date(args["menuDate"]))

        rating_row = MenuRating.query.filter_by(school=school, student=student, menu_name=args["menuName"],
                                                menu_date=str_to_date(args["menuDate"])) \
            .filter(MenuRating.star.isnot(None)).first()
        if rating_row is not None:
            return {"message": "이미 평가한 메뉴입니다."}, 404

        rating_row = MenuRating(
            school = school,
            student = student,
            menu_name= args["menuName"],
            menu_date = str_to_date(args["menuDate"]),
            star = args["star"],
            banned = False,
            rating_date = datetime.now()
        )
        db.session.add(rating_row)
        db.session.commit()


        return lunch_meal_data
