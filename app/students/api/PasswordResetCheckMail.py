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



class PasswordResetCheckMail(Resource):
    @return_500_if_errors
    def post(self):

        """
        비밀번호 인증 코드 메일 전송
        :return:
        200 : OK
        400 : 파라미터 무효
        404 : 해당 이메일 존재 X
        410 : 비밀번호 코드 인증 횟수(5번) 초과, 잠시 후 시도
        """

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