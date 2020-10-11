import marshmallow

from app.common.decorator import login_required, return_500_if_errors
from app.common.function import *
from sqlalchemy.orm import subqueryload

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate

from app.social.form import *
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


class _Search(Resource):

    @return_500_if_errors
    @login_required
    def get(self):
        student_id = g.user_id
        args = request.args
        print(args)
        try:

            args = SocialSearchQuerySchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        school_list_data = get_school_by_school_name(args["query"])

        student_query_result = []

        if school_list_data is None:
            school_query_result = None
            school_id_list = []
            school_seq_list = []
        else:
            school_list_data = school_list_data[:10]
            school_id_list = [int(school["schoolId"]) for school in school_list_data]
            print(school_id_list)
            school_rows = School.query.filter(School.school_id.in_(school_id_list)).all()

            school_query_result = [
                {**school, "schoolSeq": None} for school in school_list_data
            ]
            school_seq_list = []
            for school_row in school_rows:
                for i, school in enumerate(school_query_result):
                    if int(school["schoolId"]) == school_row.school_id:
                        print(school)
                        school_query_result[i]["schoolSeq"] = school_row.school_seq
                school_seq_list.append(school_row.school_seq)
            school_query_result.sort(key=lambda x: -1 if x["schoolSeq"] is None else 1, reverse=True)

        print(school_query_result)

        student_rows = Student.query.options(subqueryload(Student.school)).filter(Student.school_seq.in_(school_seq_list)).all()
        print(student_rows)

        for student_row in student_rows:
            student_query_result.append({
                "studentSeq" : student_row.student_seq,
                "nickname": student_row.nickname,
                "schoolName": student_row.school.name,
                "schoolSeq": student_row.school.school_seq,
            })

        student_rows = Student.query.options(subqueryload(Student.school)).filter(Student.nickname.like("%" + args["query"] + "%")).all()

        for student_row in student_rows:
            student_query_result.append({
                "studentSeq": student_row.student_seq,
                "nickname": student_row.nickname,
                "schoolName": student_row.school.name,
                "schoolSeq": student_row.school.school_seq,
            })

        student_query_result = list_remove_duplicate_dict(student_query_result)

        return {
            "data": {
                "schools": school_query_result,
                "students": student_query_result
            }
        }
