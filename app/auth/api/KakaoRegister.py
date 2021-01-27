import marshmallow

from app.common.decorator import return_500_if_errors
from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from flask import request
import jwt

from app.students.form import StudentSchema
from config import SECRET_KEY
from datetime import datetime
from datetime import timedelta
import json
import requests

from app.common.function import verify_kakao_token


class KakaoRegister(Resource):

    @return_500_if_errors
    def post(self):
        """
        카카오 계정 회원가입
        카카오 액세스 토큰과 회원가입 데이터를 함께 json으로 받는다.
        :return:
        201 : OK
        400 : 파라미터 무효
        404 : 학교 없음
        409 : 이미 존재하는 별명 or 카카오 ID
        """

        args = request.get_json()
        access_token = args["accessToken"]

        # del args["accessToken"]

        user_info = verify_kakao_token(access_token)

        print(user_info)
        # return

        if user_info is not None:
            try:

                args["id"] = "abc@naver.com"
                args["password"] = "samplepw987!"
                # 카카오 회원가입에서 아이디와 비밀번호를 받지 않으므로 ValidationError 가 발생하지 않게 임의로 넣어줬습니다.
                print(args)
                data = StudentSchema().load(args)
            except marshmallow.exceptions.ValidationError as e:
                print(e.messages)
                return {"message": "파라미터 값이 유효하지 않습니다.lkk"}, 400
            if not (1 <= data["school_grade"] <= 6) or not (1 <= data["school_class"] <= 30):
                return {"message": "파라미터 값이 유효하지 않습니다."}, 400

            same_identity_count = Student.query.filter(
                (Student.kakao_id == str(user_info["id"])) | (Student.nickname == data["nickname"])).count()
            if same_identity_count > 0:
                return {"message": "이미 존재하는 별명이거나 카카오 ID입니다."}, 409

            school_row = School.query.filter_by(school_id=data["school_id"]).first()
            if school_row is None:
                url = f"https://open.neis.go.kr/hub/schoolInfo?&SD_SCHUL_CODE={data['school_id']}&Type=json"
                response = requests.request("GET", url)

                school_data = json.loads(response.text)

                if "schoolInfo" not in school_data:
                    return {"message": "학교를 찾을 수 없습니다."}, 404

                school_data = school_data["schoolInfo"][1]["row"][0]

                school_row = School(
                    school_id=school_data["SD_SCHUL_CODE"],
                    name=school_data["SCHUL_NM"],
                    is_admin_exist=False,
                    region=school_data["LCTN_SC_NM"],
                    address=school_data["ORG_RDNMA"],
                    type=school_data["SCHUL_KND_SC_NM"]

                )

                db.session.add(school_row)
                db.session.commit()

                print(school_row.school_seq)

            if school_row.verify_code is not None:
                if "school_code" not in data or data["school_code"] != school_row.verify_code:
                    school_verified = False
                else:
                    school_verified = True

                    # return {"message": "학교 인증 코드가 일치하지 않습니다."}, 403
            else:
                school_verified = False

            # print(salt)
            if user_info["kakao_account"]["gender_needs_agreement"] is True:
                gender = None,
            else:
                try:
                    gender = user_info["kakao_account"]["gender"]
                except:
                    gender = None

            student_row = Student(
                kakao_id=user_info["id"],
                gender=gender,
                nickname=data["nickname"],
                school_grade=data["school_grade"],
                school_class=data["school_class"],
                register_date=datetime.now(),
                point=0,
                school_verified=school_verified,
                school_seq=school_row.school_seq
            )
            db.session.add(student_row)
            db.session.commit()
            return {"data":
                {
                    "id": student_row.id,
                    "nickname": student_row.nickname
                }
                   }, 201
        else:
            return {"message": "토큰이 올바르지 않습니다."}, 400
