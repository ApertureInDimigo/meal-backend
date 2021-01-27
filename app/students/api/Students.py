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
        """
        일반 회원가입
        :return:
        201 : OK
        400 : 파라미터 무효
        404 : 학교 없음
        409 : 이미 존재하는 별명 or 이메일
        """


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
