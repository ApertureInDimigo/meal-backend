import threading
from datetime import timedelta


import marshmallow

from app.common.decorator import return_500_if_errors, login_required
from app.common.function import send_mail, get_identify

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate
from app.students.form import *

from flask import request, render_template
import requests
import json


from app.redis import rd
from config import SECRET_KEY, ACCESS_TOKEN_LIFE, REFRESH_TOKEN_LIFE



class PasswordResetCheckCode(Resource):
    @return_500_if_errors
    def post(self):
        import random
        import datetime

        import jwt
        args = request.get_json()
        print(args)

        try:
            data = EmailCodeSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        wrong_count = rd.get(f"password_code:{data['id']}:wrong")
        if wrong_count is not None and int(wrong_count) >= 5:
            return {"message": "5회 실패하였습니다."}, 410

        student_row = Student.query.filter_by(id=data["id"]).first()
        if student_row is None:
            return {
                       "message": "해당 이메일이 존재하지 않습니다."
                   }, 404

        if rd.exists(f"password_code:{data['id']}") == 1:
            verify_code = rd.get(f"password_code:{data['id']}")
            print(verify_code)
            if int(verify_code) == data["code"]:

                school = student_row.school

                payload = {
                    "data":
                        {
                            "userSeq": student_row.student_seq,
                            "type": "normal",
                            "id": student_row.id,
                            "nickname": student_row.nickname,
                            "school": {
                                "schoolName": school.name,
                                "schoolId": school.school_id,
                                "schoolGrade": student_row.school_grade,
                                "schoolClass": student_row.school_class,
                            }
                        },

                }

                access_token = jwt.encode(
                    dict(payload, **{"exp": datetime.datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_LIFE)}),
                    SECRET_KEY, "HS256").decode("UTF-8")
                refresh_token = jwt.encode(
                    dict(payload,
                         **{"exp": datetime.datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_LIFE), "refresh": True}),
                    SECRET_KEY, "HS256").decode("UTF-8")
                return {"accessToken": access_token, "refreshToken": refresh_token}, 200
            else:
                if rd.exists(f"password_code:{data['id']}:wrong") == 1:
                    try:
                        rd.set(f"password_code:{data['id']}:wrong", int(wrong_count) + 1,
                               datetime.timedelta(minutes=10))
                    except:
                        rd.set(f"password_code:{data['id']}:wrong", 1, datetime.timedelta(minutes=10))

                else:
                    rd.set(f"password_code:{data['id']}:wrong", 1, datetime.timedelta(minutes=10))

                return {"message": "인증 코드가 올바르지 않습니다.", "wrongCount" : int(wrong_count) + 1}, 401
        else:
            return {"message": "인증 코드가 만료되었습니다."}, 410
