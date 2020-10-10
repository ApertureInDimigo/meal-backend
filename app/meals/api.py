import marshmallow

from app.common.decorator import login_required, return_500_if_errors
from app.common.function import *

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate

from app.meals.form import RatingStarSchema, MenuDateSchema, RatingQuestionSchema, \
    MenuDateSeqSchema, MonthDaySchema
from app.students.form import *

from flask import request, g
import requests
import json

from datetime import datetime
from statistics import mean
import numpy as np
from collections import defaultdict
from sqlalchemy import extract
from sample.menu_classifier import classify_menu


class _Menu(Resource):
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

        student, school = get_identify(student_id)
        lunch_meal_data = get_day_meal(school, args["menu_date"])
        return {
            "data": lunch_meal_data
        }


class _RatingStar(Resource):
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

        student, school = get_identify(student_id)

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=0) \
            .filter(MenuRating.star.isnot(None)).first()
        if old_rating_row is None:
            return {"message": "평가한 후에 별점을 볼 수 있습니다."}, 409

        rating_rows = MenuRating.query.filter_by(school=school, menu_date=str_to_date(args["menu_date"]),
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
            if menu["menu_name"] in lunch_meal_data and lunch_meal_data[menu["menu_seq"]] == menu["menu_name"]:
                if 1 <= menu["star"] <= 5:
                    rating_row = MenuRating(
                        school=school,
                        student=student,
                        menu_seq=menu["menu_seq"],
                        menu_name=lunch_meal_data[index],
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


class _RatingQuestion(Resource):
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

        student, school = get_identify(student_id)
        lunch_meal_data = get_day_meal(school, args["menu_date"])

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
                        "questionSeq": question_row.question_seq,
                        "content": question_row.content,
                        "options": question_row.options
                    }

                    for question_row in question_rows]})

        return {
            "data": question_dict
        }


class _RatingAnswer(Resource):
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

        student, school = get_identify(student_id)

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=args["menu_seq"]) \
            .filter(MenuRating.questions.isnot(None)).first()
        if old_rating_row is None:
            return {"message": "평가한 후에 별점을 볼 수 있습니다."}, 409
        from sqlalchemy.orm import load_only
        rating_rows = MenuRating.query.options(
            load_only("menu_name", "questions")
        ).filter_by(
            school=school, menu_date=str_to_date(args["menu_date"]),
            menu_seq=args["menu_seq"],
            banned=False).filter(MenuRating.questions.isnot(None)).all()

        answer_results = dict_mean([rating_row.questions for rating_row in rating_rows])
        print(answer_results)
        return {
                   "data": {
                       "menuSeq": args["menu_seq"],
                       "menuName": rating_rows[0].menu_name,
                       "answers":
                           [{"questionSeq": int(question_seq), "answerMean": answer_mean,
                             "options": MealRatingQuestion.query.filter_by(question_seq=question_seq).first().options}
                            for question_seq, answer_mean in answer_results.items()],

                   }
               }, 200

    @return_500_if_errors
    @login_required
    def post(self):
        student_id = g.user_id
        args = request.get_json()

        try:
            args = RatingQuestionSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify(student_id)

        menu = args["menu"]
        menu_seq = menu["menu_seq"]
        # menu_name = menu["menu_name"]
        questions = menu["questions"]

        lunch_meal_data = get_day_meal(school, args["menu_date"])

        if not (0 <= menu_seq <= len(lunch_meal_data) - 1):
            return {"message": "급식을 찾을 수 없습니다."}, 404

        menu_name = lunch_meal_data[menu_seq]

        old_rating_row = MenuRating.query.filter_by(school=school, student=student, menu_seq=menu_seq,
                                                    menu_date=str_to_date(args["menu_date"])) \
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
                     question_row.question_seq == question["question_seq"]][0]

            except Exception as e:
                return {"message": "잘못된 질문입니다."}, 404

            if not (1 <= question["answer"] <= len(target_question_row.options)):
                return {"message": "질문에 대한 잘못된 응답입니다."}, 404

        rating_row = MenuRating(
            school=school,
            student=student,
            menu_seq=menu_seq,
            menu_name=menu_name,
            menu_date=str_to_date(args["menu_date"]),
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


class _RatingFavorite(Resource):
    @return_500_if_errors
    @login_required
    def get(self):
        student_id = g.user_id
        args = request.args
        print(args)
        try:
            args = MonthDaySchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify(student_id)

        rating_rows = db.session.query().with_entities(MenuRating.menu_name).filter_by(school=school,
                                                                                       student=student).filter(
            MenuRating.is_favorite.isnot(None)).all()
        favorite_name_list = [rating_row.menu_name for rating_row in rating_rows]
        # return

        lunch_meal_list_data = get_month_meal(school, args["year"], args["month"])

        print(lunch_meal_list_data)
        print(favorite_name_list)

        favorite_dict = defaultdict(list)

        for date, menus in lunch_meal_list_data.items():
            for menu in menus:
                if menu in favorite_name_list:
                    favorite_dict[date].append(menu)
        

        return {
            "data": favorite_dict
        }, 200

    @return_500_if_errors
    @login_required
    def post(self):

        student_id = g.user_id
        args = request.get_json()
        try:

            args = MenuDateSeqSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify(student_id)
        lunch_meal_data = get_day_meal(school, args["menu_date"])

        # if args["menuName"] not in lunch_meal_data:
        #     return {"message": "급식이 존재하지 않습니다."}, 404

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=0) \
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

        student_id = g.user_id
        args = request.get_json()
        try:

            args = MenuDateSeqSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student, school = get_identify(student_id)
        lunch_meal_data = get_day_meal(school, args["menu_date"])

        # if args["menuName"] not in lunch_meal_data:
        #     return {"message": "급식이 존재하지 않습니다."}, 404

        old_rating_row = MenuRating.query.filter_by(school=school, student=student,
                                                    menu_date=str_to_date(args["menu_date"]), menu_seq=0) \
            .filter(MenuRating.is_favorite.isnot(None)).first()
        if old_rating_row is None:
            return {"message": "좋아하지 않는 메뉴입니다."}, 409

        db.session.delete(old_rating_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200
