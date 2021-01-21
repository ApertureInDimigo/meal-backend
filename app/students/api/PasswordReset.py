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

class PasswordReset(Resource):
    @return_500_if_errors
    @login_required
    def put(self):

        """
        비밀번호 재설정이 이루어짐.
        메일 코드 인증 후 받는 accessToken이 Bearer <token> 형식으로 헤더에 있어야 함(로그인 할 때처럼).
        :return:
        200 : OK
        400 : 파라미터 무효
        401 : 회원 정보 이상
        """

        args = request.get_json()
        print(args)

        try:
            data = PasswordSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        password_salt = bcrypt.gensalt()
        # print(salt)

        new_password = bcrypt.hashpw(data["password"].encode('UTF-8'), password_salt).decode('UTF-8')

        student.password = new_password
        student.password_salt = password_salt

        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200
