import marshmallow

from app.board.form import MealBoardSchema
from app.common.decorator import login_required
from app.common.function import get_day_meal, get_identify
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


class _MealBoard(Resource):

    def get(self):
        # 글 리스트 전부 가져오기
        pass

    @login_required
    def post(self):
        student_id = g.user_id
        args = request.get_json()
        try:

            args = MealBoardSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        print(args)
        student, school = get_identify(student_id)
        lunch_meal_data = get_day_meal(school, args["menu_date"])

        post_row = MealBoard(
            school=school,
            student=student,
            menus=lunch_meal_data,
            menu_date = args["menu_date"],
            post_date=datetime.now(),
            title=args["title"],
            content=args["content"],
            banned = False,
        )
        db.session.add(post_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200



class _MealBoardDetail(Resource):

    def get(self, post_seq):
        # post_seq번째 글만 가져옴
        pass

    def delete(self, post_seq):
        # 글 삭제
        pass


class _MealBoardLike(Resource):

    def post(self):
        # 좋아요 / 좋아요 취소
        pass
