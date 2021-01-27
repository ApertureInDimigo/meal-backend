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
class RatingAnswer(Resource):
    @return_500_if_errors
    @login_required
    def get(self):

        """
        급식 질문에 대한 평균 응답 결과 보여줌
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        404 : 해당 메뉴에 대해 응답된 질문이 없음
        409 : 아직 평가를 하지 않음(평가 후에 다른 사람들의 응답 결과를 보여 줌)
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

        if is_same_date(datetime.now(), str_to_date(args["menu_date"])):
            old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                        menu_date=str_to_date(args["menu_date"]),
                                                        menu_seq=args["menu_seq"], menu_time=args["menu_time"]).filter(
                MenuRating.questions.isnot(None)).first()

            if old_rating_row is None:
                return {"message": "평가한 후에 응답 결과를 볼 수 있습니다."}, 409

        from sqlalchemy.orm import load_only
        rating_rows = MenuRating.query.options(
            load_only("menu_name", "questions")
        ).filter_by(
            school=school, menu_date=str_to_date(args["menu_date"]),
            menu_seq=args["menu_seq"], menu_time=args["menu_time"],
            banned=False).filter(MenuRating.questions.isnot(None)).all()

        answer_results = dict_mean([rating_row.questions for rating_row in rating_rows])

        if len(answer_results) == 0:
            return {"message": "응답된 질문이 없습니다."}, 404

        print(answer_results)
        question_rows_data = cache.get("question_rows_data")

        answers = []
        for question_seq, answer_mean in answer_results.items():
            for question_row in question_rows_data:
                if question_row["question_seq"] == int(question_seq):
                    answers.append({"questionSeq": int(question_seq), "answerMean": answer_mean,
                                    "options": question_row["options"], "content": question_row["content"]
                                    })
                continue

        return {
                   "data": {
                       "menuSeq": args["menu_seq"],
                       "menuName": rating_rows[0].menu_name,
                       "answers":
                           answers,

                   }
               }, 200

    @return_500_if_errors
    @login_required
    def post(self):

        """
        급식 질문에 대해 응답 추가
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원정보 이상
        404 : 해당 급식이 없음 or 잘못된 질문 번호 or 질문에 대한 잘못된 응답 번호
        406 : 급식 날짜 당일이 아님
        409 : 이미 평가함
        """


        student_id = g.user_id
        args = request.get_json()

        try:
            args = RatingQuestionSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        if not is_same_date(str_to_date(args["menu_date"]), datetime.now()):
            return {"message": "당일에만 평가할 수 있습니다."}, 406

        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        menu = args["menu"]
        menu_seq = menu["menu_seq"]
        # menu_name = menu["menu_name"]
        questions = menu["questions"]

        lunch_meal_data = get_day_meal(school, args["menu_date"], target_time=args["menu_time"])

        if not (0 <= menu_seq <= len(lunch_meal_data) - 1):
            return {"message": "급식을 찾을 수 없습니다."}, 404

        menu_name = lunch_meal_data[menu_seq]

        old_rating_row = MenuRating.query.filter_by(school=school, student=student, menu_seq=menu_seq,
                                                    menu_date=str_to_date(args["menu_date"]),
                                                    menu_time=args["menu_time"], ) \
            .filter(MenuRating.questions.isnot(None)).first()
        if old_rating_row is not None:
            return {"message": "이미 평가했습니다."}, 409

        question_rows = get_question_rows(menu_name)

        now = datetime.now()

        if len(question_rows) != len(questions):
            return {"message": "잘못된 질문입니다."}, 404

        for question in questions:
            # if question["question_seq"] in [question_row.question_seq for question_row in question_rows]:

            try:
                target_question_row = \
                    [question_row for question_row in question_rows if
                     question_row["question_seq"] == question["question_seq"]][0]

            except Exception as e:
                return {"message": "잘못된 질문입니다."}, 404

            if not (1 <= question["answer"] <= len(target_question_row["options"])):
                return {"message": "질문에 대한 잘못된 응답입니다."}, 404

        rating_row = MenuRating(
            school=school,
            student=student,
            menu_seq=menu_seq,
            menu_name=menu_name,
            menu_date=str_to_date(args["menu_date"]),
            menu_time=args["menu_time"],
            questions={
                str(question["question_seq"]): question["answer"] for question in questions
            },
            banned=False,
            rating_date=now
        )

        print(rating_row)

        db.session.add(rating_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200

        # for question in questions:
