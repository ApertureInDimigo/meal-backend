import threading

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

from datetime import datetime
from app.redis import rd
from config import SECRET_KEY


class Students(Resource):
    @return_500_if_errors
    def post(self):
        args = request.get_json()
        print(args)

        try:
            data = StudentSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        if not (1 <= data["school_grade"] <= 6) or not (1 <= data["school_class"] <= 30):
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        same_identity_count = Student.query.filter(
            (Student.id == data["id"]) | (Student.nickname == data["nickname"])).count()
        if same_identity_count > 0:
            return {"message": "이미 존재하는 ID나 별명입니다."}, 409

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

        school_verified = None
        if school_row.verify_code is not None:
            if "school_code" not in data or data["school_code"] != school_row.verify_code:
                school_verified = False
            else:
                school_verified = True

                # return {"message": "학교 인증 코드가 일치하지 않습니다."}, 403
        else:
            school_verified = False
        password_salt = bcrypt.gensalt()
        # print(salt)

        student_row = Student(
            id=data["id"],
            password=bcrypt.hashpw(data["password"].encode('UTF-8'), password_salt).decode('UTF-8'),
            password_salt=password_salt,
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


class IdCheck(Resource):
    @return_500_if_errors
    def get(self, id):
        # id = request.args.get("id")
        c = Student.query.filter_by(id=id).count()
        if c != 0:
            return {"message": "이미 존재하는 ID 입니다."}, 409
        else:
            return {"data":
                {
                    "id": id
                },
                       "message": "사용 가능한 ID입니다."
                   }, 200


class NicknameCheck(Resource):
    @return_500_if_errors
    def get(self, nickname):
        # nickname = request.args.get("nickname")
        c = Student.query.filter_by(nickname=nickname).count()
        if c != 0:
            return {"message": "이미 존재하는 별명 입니다."}, 409
        else:
            return {"data":
                {
                    "nickname": nickname
                },
                       "message": "사용 가능한 별명입니다."
                   }, 200


class PasswordResetCheckMail(Resource):
    @return_500_if_errors
    def post(self):
        import random
        import datetime

        args = request.get_json()
        print(args)

        try:
            data = EmailSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        wrong_count = rd.get(f"password_code:{data['id']}:wrong")
        if wrong_count is not None and int(wrong_count) >= 5:
            return {"message": "잠시 후 시도해주세요."}, 410


        student_row = Student.query.filter_by(id=data["id"]).first()
        if student_row is None:
            return {
                       "message": "해당 이메일이 존재하지 않습니다."
                   }, 404

        if rd.exists(f"password_code:{data['id']}") == 1:
            random_code = rd.get(f"password_code:{data['id']}")
        else:
            random_code = random.randint(100000, 999999)
        rd.set(f"password_code:{data['id']}", random_code, datetime.timedelta(minutes=3))
        print(random_code)

        html = render_template('./mail/password_reset.html',
                                                                       data={"verify_code": int(random_code)})
        threading.Thread(target=lambda: send_mail(receiver=data["id"], title="[YAMMEAL] 비밀번호 찾기 인증 번호",
                                                  html=html)
                         ).start()

        return {
            "message" : "정상적으로 처리되었습니다."
        }, 200


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
                    "exp": datetime.datetime.now() + datetime.timedelta(minutes=99999999)
                }

                token = jwt.encode(payload, SECRET_KEY, "HS256").decode("UTF-8")
                return {"accessToken": token}, 200
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


class PasswordReset(Resource):
    @return_500_if_errors
    @login_required
    def put(self):

        args = request.get_json()
        print(args)

        try:
            data = PasswordSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        student, _ = get_identify()

        password_salt = bcrypt.gensalt()
        # print(salt)

        new_password = bcrypt.hashpw(data["password"].encode('UTF-8'), password_salt).decode('UTF-8')

        student.password = new_password
        student.password_salt = password_salt

        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200


class IdHint(Resource):
    @return_500_if_errors
    def get(self):

        args = request.args
        print(args)

        try:
            data = NicknameSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student_row = Student.query.filter_by(nickname=data["nickname"]).first()
        if student_row is None:
            return {"message" : "닉네임을 찾을 수 없습니다."}, 404

        student_id = student_row.id
        print(student_id)
        part1, part2= student_id.split("@")
        part2, part3 = part2.split(".")

        part1 = part1[:min(3, len(part1) // 3)] + "*****"
        part2 = part2[:1] +  "****"
        part3 = len(part3) * "*"

        filtered = f"{part1}@{part2}.{part3}"
        return {
            "data" : filtered
        }



