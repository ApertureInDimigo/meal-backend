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

class RatingAnswerMy(Resource):

    @return_500_if_errors
    @login_required
    def get(self):
        """
        내가 응답한 급식 질문에 대한 평가
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        409 : 아직 평가 안 함
        """
        student_id = g.user_id
        args = request.args
        print(args)

        try:
            args = MenuDateSeqSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=args["menu_seq"],
                                                    menu_time=args["menu_time"]).filter(
            MenuRating.questions.isnot(None)).first()
        if old_rating_row is None:
            return {"message": "평가한 후에 응답 결과를 볼 수 있습니다."}, 409
        from sqlalchemy.orm import load_only
        rating_rows = MenuRating.query.options(
            load_only("menu_name", "questions")
        ).filter_by(
            school=school, menu_date=str_to_date(args["menu_date"]),
            menu_seq=args["menu_seq"], student=student, menu_time=args["menu_time"],
            banned=False).filter(MenuRating.questions.isnot(None)).first()

        question_rows_data = cache.get("question_rows_data")

        answers = []
        for question_seq, answer in rating_rows.questions.items():
            for question_row in question_rows_data:
                if question_row["question_seq"] == int(question_seq):
                    answers.append({"questionSeq": int(question_seq), "answer": answer,
                                    "options": question_row["options"], "content": question_row["content"]
                                    })
                continue

        return {
                   "data": {
                       "menuSeq": args["menu_seq"],
                       "menuName": rating_rows.menu_name,
                       "answers": answers

                   }
               }, 200