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

from app.common.function import verify_kakao_token


class KakaoLogin(Resource):

    @return_500_if_errors
    def post(self):
        """
        카카오 로그인
        카카오에서 제공한 accessToken 을 json으로 받는다.
        :return:
        200 : OK
        400 : 토큰 이상함
        404 : 카카오 회원가입이 되지 않음
        """


        args = request.get_json()
        access_token = args["accessToken"]

        user_info = verify_kakao_token(access_token)

        print(access_token)
        print(user_info)
        # return

        if user_info is not None:
            target_student = Student.query.filter_by(kakao_id=str(user_info["id"])).first()
            if target_student is None:
                return {"message": "회원가입 해주세요."}, 404
            else:
                row = target_student
                school = row.school
                payload = {
                    "data":
                        {
                            "userSeq": row.student_seq,
                            "type": "kakao",
                            "kakaoId": row.kakao_id,
                            "nickname": row.nickname,
                            "school": {
                                "schoolName": school.name,
                                "schoolId": school.school_id,
                                "schoolGrade": row.school_grade,
                                "schoolClass": row.school_class,

                            }
                        },
                }

                access_token = jwt.encode(
                    dict(payload, **{"exp": datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_LIFE)}),
                    SECRET_KEY, "HS256").decode("UTF-8")
                refresh_token = jwt.encode(
                    dict(payload, **{"exp": datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_LIFE), "refresh": True}),
                    SECRET_KEY, "HS256").decode("UTF-8")
                return {"accessToken": access_token, "refreshToken": refresh_token}, 200

        else:
            return {"message": "토큰이 올바르지 않습니다."}, 400
