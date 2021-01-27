import marshmallow

from app.common.decorator import return_500_if_errors
from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from flask import request
import jwt

from app.students.form import StudentSchema
from config import SECRET_KEY, ACCESS_TOKEN_LIFE, REFRESH_TOKEN_LIFE
from datetime import datetime
from datetime import timedelta
import json
import requests


class Auth(Resource):

    @return_500_if_errors
    def get(self):
        """
        토큰이 유효한 지 확인하고, 유효하면 사용자 정보를 반환한다.
        :return:
        200 : OK
        400 : 토큰 미 입력
        401 : 토큰이 이상함
        """

        if request.headers.get('Authorization') is None:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        access_token = request.headers.get('Authorization').split()
        if len(access_token) < 2:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        access_token = access_token[1]

        if access_token is not None:
            try:
                payload = jwt.decode(access_token, SECRET_KEY, "HS256")
            except jwt.InvalidTokenError:
                payload = None

            if payload is None:
                return {"message": "토큰이 유효하지 않습니다."}, 401

            return payload, 200

        else:

            return {"message": "로그인 토큰이 필요합니다."}, 400

    @return_500_if_errors
    def post(self):
        """
        아이디와 비밀번호를 통해 로그인한다.
        :return:
        200 : 정상적인 로그인
        """

        args = request.get_json()
        row = Student.query.filter_by(id=args["id"]).first()
        if row and bcrypt.checkpw(args["password"].encode("UTF-8"), row.password.encode("UTF-8")):

            school = row.school

            payload = {
                "data":
                    {
                        "userSeq": row.student_seq,
                        "type": "normal",
                        "id": row.id,
                        "nickname": row.nickname,
                        "school": {
                            "schoolName": school.name,
                            "schoolId": school.school_id,
                            "schoolGrade": row.school_grade,
                            "schoolClass": row.school_class,
                        }
                    },

            }

            access_token = jwt.encode(dict(payload , **{"exp": datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_LIFE)}),
                                      SECRET_KEY, "HS256").decode("UTF-8")
            refresh_token = jwt.encode(
                dict(payload , **{"exp": datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_LIFE), "refresh": True}),
                SECRET_KEY, "HS256").decode("UTF-8")
            return {"accessToken": access_token, "refreshToken": refresh_token}, 200
        else:
            return {"message": "ID나 비밀번호가 옳지 않습니다."}, 404


