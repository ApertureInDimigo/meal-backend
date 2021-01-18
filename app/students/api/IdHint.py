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

        if student_id is None:
            return {"message": "소셜 로그인 회원입니다"}, 401

        part1, part2= student_id.split("@")
        part2, part3 = part2.split(".")

        part1 = part1[:min(3, len(part1) // 3)] + "*****"
        part2 = part2[:1] +  "****"
        part3 = len(part3) * "*"

        filtered = f"{part1}@{part2}.{part3}"
        return {
            "data" : filtered
        }


