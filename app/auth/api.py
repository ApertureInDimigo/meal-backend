import marshmallow

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

# server.py

class Auth(Resource):

    def get(self):
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

    def post(self):
        args = request.get_json()
        row = Student.query.filter_by(id=args["id"]).first()
        if row and bcrypt.checkpw(args["password"].encode("UTF-8"), row.password.encode("UTF-8")):

            school = row.school

            payload = {
                "data":
                    {
                        "id": row.id,
                        "nickname": row.nickname,
                        "school": {
                            "schoolName": school.name,
                            "schoolId": school.school_id,
                            "schoolGrade": row.school_grade,
                            "schoolClass": row.school_class
                        }
                    },
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 3)
            }

            token = jwt.encode(payload, SECRET_KEY, "HS256").decode("UTF-8")
            return {"accessToken": token}, 200
        else:
            return {"message": "ID나 비밀번호가 옳지 않습니다."}, 404


def verify_kakao_token(access_token):
    if access_token is None or type(access_token) != str:
        return None

    # access_token = "Sdfa"

    res = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization": "Bearer " + access_token})
    res_status = res.status_code
    if res_status == 401:
        return None
    elif res_status == 200:
        return json.loads(res.text)


class KakaoLogin(Resource):
    def post(self):
        args = request.get_json()
        access_token = args["accessToken"]

        user_info = verify_kakao_token(access_token)

        print(access_token)
        print(user_info)
        # return


        if user_info is not None:
            target_student = Student.query.filter_by(kakao_id=str(user_info["id"])).first()
            if target_student is None:
                return {"message" : "회원가입 해주세요."}, 404
            else:
                row = target_student
                school = row.school
                payload = {
                    "data":
                        {
                            "kakaoId": row.kakao_id,
                            "nickname": row.nickname,
                            "school": {
                                "schoolName": school.name,
                                "schoolId": school.school_id,
                                "schoolGrade": row.school_grade,
                                "schoolClass": row.school_class
                            }
                        },
                    "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 3)
                }

                token = jwt.encode(payload, SECRET_KEY, "HS256").decode("UTF-8")
                return {"accessToken": token}, 200

        else:
            return {"message": "토큰이 올바르지 않습니다."}, 400


class KakaoRegister(Resource):
    def post(self):
        args = request.get_json()
        access_token = args["accessToken"]

        # del args["accessToken"]



        user_info = verify_kakao_token(access_token)

        print(user_info)
        # return

        if user_info is not None:
            try:

                args["id"] = "sampleid123"
                args["password"] = "samplepw987!"
                # 카카오 회원가입에서 아이디와 비밀번호를 받지 않으므로 ValidationError 가 발생하지 않게 임의로 넣어줍니다.
                print(args)
                data = StudentSchema().load(args)
            except marshmallow.exceptions.ValidationError as e:
                print(e.messages)
                return {"message": "파라미터 값이 유효하지 않습니다.lkk"}, 400
            if not (1 <= data["school_grade"] <= 6) or not (1 <= data["school_class"] <= 30):
                return {"message": "파라미터 값이 유효하지 않습니다."}, 400

            same_identity_count = Student.query.filter((Student.kakao_id == str(user_info["id"])) | (Student.nickname == data["nickname"])).count()
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
                    return {"message": "학교 인증 코드가 일치하지 않습니다."}, 403


            # print(salt)
            if user_info["kakao_account"]["gender_needs_agreement"] is True:
                gender = None,
            else:
                gender = user_info["kakao_account"]["gender"]


            student_row = Student(
                kakao_id= user_info["id"],
                gender= gender,
                nickname=data["nickname"],
                school_grade=data["school_grade"],
                school_class=data["school_class"],
                register_date=datetime.now(),
                point=0,
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
